from bge import logic as gl
from .evertClass import *
from . import OSC
import socket

class Evertims():
    """
    Main EVERTims python module. Send scene information
    (room geometry, materials, listener and source position, etc.)
    to EVERTims client. Eventually trace rays received from EVERTims
    client (for debug purpose).
    """

    def __init__(self):
        """
        EVERTims class constructor
        """

        # define dict to store EVERTims elements in the scene,
        # involved in the simulation
        self.rooms = dict()     # store scene's rooms
        self.sources = dict()   # store scene's sources
        self.listeners = dict() # store scene's listeners

        # define parameters related to raytracing visual feedback
        self.traceRays = False      # enable/disable visual feedback
        self.rayManager = None   # raytracing handler

        # define debug flag
        self.dbg = True # print info in console if set to True

        # define network related parameters
        self.connect = {
        'raw_msg': '',              # To be filled in threading, contains raw socket datas awaiting to be processed (faster to forbid Evertims msg jamming the socket)
        'ip_evert': 'localhost',    # IP of EVERTims' computer
        'ip_local': 'localhost',    # IP of Blender's computer
        'port_w': 0,                # Port to write in EVERTims
        'port_r': 0,                # Port to read from EVERTims
        'socket': None,             # socket to receive msg from EVERTims
        'socket_size': 2*1024,      # Size of reader socket (a_min = 124, v_min = ..?)
        'socket_timeout': 1e-5,     # Timeout of reader socket
        'buffer_size': 0,           # Buffer size (socket buffer) process will discard packets to receive new ones - no packet discarded if 0 (RealTime / NoError mode)
        }

    def __del__(self):
        """
        EVERTims class destructor
        """
        # close socket used for raytracing feedback if option was enabled
        if self.traceRays:
            if self.dbg: print('closing read socket (the one used for raytracing feedback)')
            self.connect['socket'].close()

    def setDebugMode(self, setDebug):
        """
        Enable / disable debug mode (print info in console).

        :param setDebug: enable/disable debug mode
        :type setDebug: Bool
        """
        self.dbg = setDebug

    def addRoom(self, obj):
        """
        Add KX_GameObject as EVERTims room in local dictionnary.

        :param obj: room to add in local dict
        :type obj: KX_GameObject
        """
        self.rooms[obj.name] = Room(obj)

    def addSource(self, obj):
        """
        Add KX_GameObject as EVERTims source in local dictionnary.

        :param obj: source to add in local dict
        :type obj: KX_GameObject
        """
        self.sources[obj.name] = SourceListener(obj, 'source')

    def addListener(self, obj):
        """
        Add KX_GameObject as EVERTims listener in local dictionnary.

        :param obj: listener to add in local dict
        :type obj: KX_GameObject
        """
        self.listeners[obj.name] = SourceListener(obj, 'listener')

    def initConnection_read(self, ip, port):
        """
        Init EVERTims to Blender connection, used to receive raytracing information.

        :param ip: IP adress of local host running the BGE
        :param port: PORT where to read information sent by EVERTims client
        :type ip: String
        :type port: Integer
        """
        self.connect['port_r'] = port
        self.connect['ip_local'] = ip

    def initConnection_write(self, ip, port):
        """
        Init Blender to EVERTims connection, used to send room, source, listener, etc. information

        :param ip: IP adress of client host running EVERTims
        :param port: PORT where to write information sent to EVERTims client
        :type ip: String
        :type port: Integer
        """
        self.connect['port_w'] = port
        self.connect['ip_evert'] = ip

    def isReady(self):
        """
        Check EVERTims minimum requirements to enable simulation start:
        at least 1 room, 1 listener, 1 source, and initConnection_write
        parameters must have been defined.
        """
        if self.rooms and self.sources and self.listeners \
            and self.connect['port_w'] and self.connect['ip_evert']:
            return True
        else:
            return False

    def updateClient(self, objType = ''):
        """
        Upload Room, Source, and Listener information to EVERTims client.

        :param objType: which type of object to update: either 'room', 'source', 'listener', or 'mobile' (i.e. 'source' and 'listener')
        :type objType: String
        """
        if (objType == 'room') or not objType:
            for roomName, room in self.rooms.items():
                msgList = room.getPropsListAsOSCMsgs()
                for msg in msgList:
                    self._sendOscMsg(self.connect['ip_evert'],self.connect['port_w'],msg)

        if (objType == 'source') or (objType == 'mobile') or not objType:
            for sourceName, source in self.sources.items():
                if source.hasMoved():
                    msg = source.getPropsAsOSCMsg()
                    self._sendOscMsg(self.connect['ip_evert'],self.connect['port_w'],msg)

        if (objType == 'listener') or (objType == 'mobile') or not objType:
            for listenerName, listener in self.listeners.items():
                if listener.hasMoved():
                    msg = listener.getPropsAsOSCMsg()
                    self._sendOscMsg(self.connect['ip_evert'],self.connect['port_w'],msg)

    def setMovementUpdateThreshold(self, thresholdLoc, thresholdRot):
        """
        Define a threshold value to limit listener / source update to EVERTims client.

        :param thresholdLoc: value (m) above which an EVERTims object as to move to be updated to the client
        :param thresholdRot: value (deg) above which an EVERTims object as to rotate to be updated to the client
        :type thresholdLoc: Float
        :type thresholdRot: Float
        """
        for sourceName, source in self.sources.items():
            source.setMoveThreshold(thresholdLoc, thresholdRot)
        for listenerName, listener in self.listeners.items():
            listener.setMoveThreshold(thresholdLoc, thresholdRot)

    def startClientSimulation(self):
        """
        Start EVERTims simulation: sent '/facefinished' message to EVERTims client
        to start acoustic calculation, add local pre_draw method to BGE scene stack.
        """
        # send room, listener, source info to EVERTims client
        self.updateClient()
        # send '/facefinished' to EVERTims client (start calculations)
        self._sendOscMsg(self.connect['ip_evert'],self.connect['port_w'],'/facefinished')
        # add local pre_draw method to to scene callback
        gl.getCurrentScene().pre_draw.append(self._pre_draw)

    def activateRayTracingFeedback(self, shouldTraceRays):
        """
        Enable / disable visual feedback on EVERTims raytracing.
        Will init read socket to receive raytracing messages if set to True.

        :param shouldTraceRays: activate / deactivate option
        :type shouldTraceRays: Bool
        """
        # check if connection parameters have been defined
        if not shouldTraceRays:
            self.traceRays = False
            # TODO: disable self.rayManager

        else:
            managedToConnect = False
            if self.connect['ip_local'] and self.connect['port_r']:

                # init receive socket
                (self.connect['socket'], isConnected) = self._getOscSocket(self.connect['ip_local'], self.connect['port_r'])
                if isConnected:

                    # RayManager will handle receiving of raytracing messages,
                    # drawing of rays in BGE
                    self.rayManager = RayManager(self.connect['socket'], self.connect['socket_size'], self.dbg)
                    managedToConnect = True

            if managedToConnect:
                self.traceRays = True
            else:
                print('### Cannot establish downlink connection to EVERTims server, Raytracing feedback deactivated')

    def _pre_draw(self):
        """
        Method added to scene pre_draw stack,
        called before rendering each frame in BGE.
        """
        # update listener / source position in Client
        self.updateClient('mobile')

    def _getOscSocket(self, ip,host):
        """
        Initialise a socket at host@ip.

        :param ip: IP adress to connect socket
        :param port: PORT to connect socket
        :type ip: String
        :type port: Integer
        :return: (socket, isconnected)
        :rtype: Socket, Bool
        """
        # create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # eventually set socket buffer size (up speed for real-time)
        if self.connect['buffer_size']:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.connect['buffer_size'])
            print ('!!! socket.SO_RCVBUF size set to', self.connect['buffer_size'], '-> expect droped (unprocessed) packets')

        # bind socket
        isConnected = False
        try:
            sock.bind((ip, host))
            sock.setblocking(0)
            sock.settimeout(self.connect['socket_timeout'])
            isConnected = True
        except OSError as e:
            print ('###', e)
        return (sock, isConnected)

    def _sendOscMsg(self, ip, host, header, msg = ''):
        """
        Send OSC 'header msg' at host@ip.

        :param ip: IP adress where to send OSC message
        :param port: PORT where to send OSC message
        :param header: OSC message header
        :param msg: OSC message content
        :type ip: String
        :type port: Integer
        :type header: String
        :type msg: String
        """
        # create OSC client
        client = OSC.OSCClient()
        # create OSC message, set address, fill message
        osc_msg = OSC.OSCMessage()
        osc_msg.setAddress(header)
        osc_msg.append(msg)

        # send OSC message
        try:
            client.sendto(osc_msg,(ip,host))
            if self.dbg: print ('-> sent to ' + str(host) + '@' + ip + ': ' + header + ' ', msg, '\n')
        except TypeError:
            print ('!!! no route to', host, ip, 'to send OSC message:', header.split(' ')[0]) # may occur in OSC.py if no route to host
