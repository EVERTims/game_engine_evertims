from bge import logic as gl
from . import OSC
import mathutils
import math
import socket
import bgl

class Ray():
    """
    Ray object, used for raytracing visual feedback. Basically a start point, an
    end point and a drawing method based on bgl (GLSL)
    """

    def __init__(self, ID, p1, p2):
        """
        Ray class constructor.

        :param ID: ray ID
        :param p1: ray start point coordinates
        :param p2: ray end point coordinates
        :type ID: Integer
        :type p1: 3-elements tuple
        :type p2: 3-elements tuple
        """

        self.ID = ID
        self.p1 = p1
        self.p2 = p2

    def setCoord(self, p1, p2):
        """
        Define ray coordinates.

        :param p1: ray start point coordinates
        :param p2: ray end point coordinates
        :type p1: 3-elements tuple
        :type p2: 3-elements tuple
        """

        self.p1 = p1
        self.p2 = p2

    def drawPath(self):
        """
        Draw ray on screen.
        """
        bgl.glColor4f(0.8,0.8,0.9,0.01)
        bgl.glLineWidth(0.01)

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex3f(self.p1[0],self.p1[1],self.p1[2])
        bgl.glVertex3f(self.p2[0],self.p2[1],self.p2[2])
        bgl.glEnd()

        bgl.glNormal3f(0.0,0.0,1.0)
        bgl.glShadeModel(bgl.GL_SMOOTH);


class Room():
    """
    Room object, bridge between the notions of BGE KX_GameObject and EVERTims room.
    """

    def __init__(self, kx_obj):
        """
        Room constructor.

        :param kx_obj: Blender Object representing EVERTims room
        :type kx_obj: KX_GameObject
        """
        self.obj = kx_obj
        # TODO: ADD GLOBAL NUMBERING ON '...' PROPERTY (TO AVOID 2 OBJECTS HAVING THE SAME)
        if not 'room' in self.obj:
            self.obj['room'] = 0

    def getPropsListAsOSCMsgs(self):
        """
        Return a list of OSC formatted messages holding room properties
        (faces geometry and associated materials).

        :return: list of strings, formatted as OSC messages ready to be sent to EVERTims Client
        :rtype: List
        """
        formatedMsg = []
        polygonDict = self._getFacesAndMaterials()
        for key in polygonDict.keys():
            faceID = str(key)
            matID = polygonDict[key]['material']
            p0123 = polygonDict[key]['vertices']
            msg = self._shapeFaceMsg(faceID,matID,p0123)
            formatedMsg.append(msg)
        return formatedMsg

    def _getFacesAndMaterials(self):
        """
        Return a dictionary which elements represent the vertices and material of a face.

        :return: dict of dict, each dict holds items representing a face: keys are 'material' (String naming the material) and 'vertices' (N-element list of the vertices that compose the face, each element of said list is a list of the vertice's coordinates).
        :rtype: Dictionary
        """
        room = self.obj
        polygonDict = {}          # a dict that holds faces (dict), their vertices (dict: positions and materials)
        mesh = room.meshes[0]     # WARNING: supposed to work with a single mesh material
        poly = mesh.getPolygon(0) # get polygon list

        for n in range(0,mesh.numPolygons):
            polygonDict[n+1] = {}

            # get face (poly) materials
            poly = mesh.getPolygon(n)
            polygonDict[n+1]['material'] = poly.material_name.replace('MA','') # since blender add 'MA' to each material name

            # get face (poly) vertices positions
            v1_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v1).XYZ
            v2_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v2).XYZ
            v3_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v3).XYZ
            v4_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v4).XYZ
            polygonDict[n+1]['vertices'] = [v1_xyz, v2_xyz, v3_xyz, v4_xyz]

            # if gl.dbg: print ('  ' + 'face ' + str(n) + ' - materials '+ poly.material_name.replace('MA',''))
        return polygonDict

    def _shapeFaceMsg(self, faceID,matID,pListVect):
        """
        String shapping (particularly for pListVect)
        """
        pList_string = ''
        for vect in pListVect:
            vectRound = [round(elmt,2) for elmt in vect[:]]
            p_string = str(vectRound[:])
            p_string = p_string.replace('[','').replace(']','').replace(',','')
            pList_string = pList_string + ' ' + p_string
        osc_msg = '/face ' + str(faceID) + ' ' + matID +  ' ' + pList_string
        return osc_msg

class SourceListener():
    """
    Source / Listener object, bridge between the notions of BGE KX_GameObject and EVERTims Listeners / Sources.
    """

    def __init__(self, kx_obj, typeOfInstance):
        """
        Source / Listener constructor.

        :param kx_obj: Blender Object representing EVERTims listener / source
        :param typeOfInstance: precision on the nature of the created object, either 'source' or 'listener'
        :type kx_obj: KX_GameObject
        :type typeOfInstance: String
        """
        self.obj = kx_obj
        self.type = typeOfInstance # either 'source' or 'listener'
        self.old_worldTransform = None
        self.moveThresholdLoc = 0.0
        self.moveThresholdRot = 0.0
        # TODO: ADD GLOBAL NUMBERING ON '...' PROPERTY (TO AVOID 2 OBJECTS HAVING THE SAME)
        if not self.type in self.obj:
            self.obj[self.type] = 0

    def setMoveThreshold(self, thresholdLoc, thresholdRot):
        """
        Define a threshold value to limit listener / source update to EVERTims client.

        :param threshold: value above which an EVERTims object as to move to be updated (in position) to the client
        :type threshold: Float
        """
        self.moveThresholdLoc = thresholdLoc
        self.moveThresholdRot = thresholdRot

    def hasMoved(self):
        """
        Check if source/client has moved since last check.

        :return: a boolean saying whether or not the source / listener moved since last check
        :rtype: Boolean
        """
        # if objed has not yet been checked
        if not self.old_worldTransform:
            self.old_worldTransform = self.obj.worldTransform.copy()
            return True

        elif self._areDifferent_Mat44(self.obj.worldTransform, self.old_worldTransform, self.moveThresholdLoc, self.moveThresholdRot):
            # moved since last check
            self.old_worldTransform = self.obj.worldTransform.copy()
            return True
        else:
            # did not move since last check
            return False

    def getPropsAsOSCMsg(self):
        """
        Return a OSC formated string holding source / lister type, name, and current world transform.

        :return: typically: '/listener listener_1 -0.76 -0.65 0.0 0.0 -0.13 0.15 0.98 0.0 -0.63 0.75 -0.19 0.0 4.62 -5.45 3.08 1.0'
        :rtype: String
        """
        msg = self._shapeOSCMsg('/' + self.type, self.type + '_' + str(self.obj[self.type]), self.obj.worldTransform)
        return msg

    def _shapeOSCMsg(self, header, ID, mat44):
        """
        String shapping (particularly for mat44).
        """
        mat44_str = ''
        for elmt in mat44.col: mat44_str = mat44_str + str(elmt.to_tuple(2)[:]) # to tuple allows to round the Vector
        mat44_str = mat44_str.replace('(','').replace(')',' ').replace(',','')
        osc_msg = header + ' ' + ID + ' ' + mat44_str
        return osc_msg

    def _areDifferent_Mat44(self, mat1, mat2, thresholdLoc = 1.0, thresholdRot = 1.0):
        """
        Check if 2 input matrices are different above a certain threshold.

        :param mat1: input Matrix
        :param mat2: input Matrix
        :param thresholdLoc: threshold above which delta translation between the 2 matrix has to be for them to be qualified as different
        :param thresholdRot: threshold above which delta rotation between the 2 matrix has to be for them to be qualified as different
        :type mat1: mathutils.Matrix
        :type mat2: mathutils.Matrix
        :type thresholdLoc: Float
        :type thresholdRot: Float
        :return: a boolean stating wheter the two matrices are different
        :rtype: Boolean
        """
        areDifferent = False
        jnd_vect = mathutils.Vector((thresholdLoc,thresholdLoc,thresholdRot))
        t1, t2 = mat1.to_translation(), mat2.to_translation()
        r1, r2 = mat1.to_euler(), mat2.to_euler()
        for n in range(3):
            if (abs(t1[n]-t2[n]) > thresholdLoc) or (abs(math.degrees(r1[n]-r2[n])) > thresholdRot): areDifferent = True
        return areDifferent

class RayManager():
    """
    Ray manager class: handle Ray objects for raytracing visual feedback.
    """

    def __init__(self, sock, sock_size, dbg = False):
        """
        Ray manager constructor.

        :param sock: socket with which the ray manager communicates with the EVERTims client.
        :param sock_size: size of packet read every pass (sock.recv(sock_size))
        :param dbg: enable debug (print log in console)
        :type sock: Socket
        :type sock_size: Integer
        :type dbg: Boolean
        """
        self.sock = sock
        self.sock_size = sock_size
        self.dbg = dbg
        self.rayDict = {}
        self.missedRayCounter = 0

        # add local pre_draw method to to scene callback
        gl.getCurrentScene().pre_draw.append(self._pre_draw)

    def _pre_draw(self):
        """
        Method added to scene pre_draw stack,
        called before rendering each frame in BGE.
        """
        # read socket content
        msg = self._readSocket()
        # add ray to local dict
        if msg:
            self._syncRayDict(msg)
        # draw rays
        self._drawRays()

    def _syncRayDict(self, msg):
        """
        Synchronize (add, update, or remove) rays from the
        local dict based on OSC messages received from EVERTims client.

        :param msg: OSC message received from EVERTims client
        :type msg: String
        """
        # check if 'on' or 'off' line
        if msg[0] == 'on':
            # check if full message received
            if len(msg) == 4 and len(msg[-1]) == 3:
                # if on, check if new line or update line
                if not msg[1] in self.rayDict:
                    # new line
                    self.rayDict[msg[1]] = Ray(msg[1],msg[2], msg[3])
                    if self.dbg: print('+ added in ray dict: ', msg, '\n')
                else:
                    # update line
                    self.rayDict[msg[1]].setCoord(msg[2], msg[3])
                    if self.dbg: print('updated line in ray dict: ', msg, '\n')
            else:
                # account for missed ray
                self.missedRayCounter += 1
                if self.dbg:
                    print('\r!!! ray(s) missed: {0}'.format(self.missedRayCounter), '\n')

        elif msg[0] == 'off':
            # remove ray from local dict
            try:
                del(self.rayDict[msg[1]])
                if self.dbg: print ('removed line in ray dict:', self.rayDict[msg[1]].ID, '\n')
            except KeyError:
                if self.dbg: print ('cannot remove ray (not in local dict):', msg, '\n')


    def _drawRays(self):
        """
        Invoke draw methods from rays in local dict
        """
        for rayID, ray in self.rayDict.items():
            ray.drawPath()


    def _readSocket(self):
        """
        Read input from socket.

        :return: OSC message as a decoded string
        :rtype: String
        """
        try:
            raw_msg = self.sock.recv(self.sock_size)

            if raw_msg:
                osc_msg = raw_msg.decode("utf-8")
                out_msg = self._shapeOscInMsg(osc_msg)
                if self.dbg: print ('<- received from', self.sock.getsockname()[0] + ':' + str(self.sock.getsockname()[1]), ':', out_msg)
                # gl.logs['in'].append(out_msg) # record OSC logs
                return out_msg
            # ''.join(total_data)
            else: return ()

        except socket.timeout: # nothing received
            return ()
        except OSError: # socket closed
            return ()

    def _shapeOscInMsg(self, msg_str):
        """
        OSC input message shapping.

        Format OUT (state, ID, (coodStart), (coordEnd))
                   ('on', 45, (2.06, 0.0, 1.67), (28.2, 0.0))

        :param msg_str: OSC input message
        :type msg_str: String
        """

        msg_list = msg_str.split(' ')

        onOff = msg_list[0][6:9].replace(' ', '')
        ID = int(msg_list[1])

        if len(msg_list) == 8 and len(msg_list[-1]) >= 4:
            coord1, coord2 = tuple([round(float(elmt),2) for elmt in msg_list[2:5]]), tuple([round(float(elmt),2) for elmt in msg_list[5::]])
        else:
            coord1, coord2 = (), ()

        return (onOff,ID,coord1,coord2)
