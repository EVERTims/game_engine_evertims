# import scripts.OSC as OSC
import scripts.OSC as OSC
import scripts.evertClass as evertClass
from bge import logic as gl
import socket
import copy
import mathutils
import sys
import copy

## Mathutils related method ------------------------------------------

def areDifferent_Mat44(mat1, mat2, JND):
	areDifferent = False
	jnd_vect = mathutils.Vector((JND,JND,JND))
	t1, t2 = mat1.to_translation(), mat2.to_translation()
	r1, r2 = mat1.to_quaternion().axis, mat2.to_quaternion().axis
	for n in range(3):
		if (abs(t1[n]-t2[n]) > JND) or (abs(r1[n]-r2[n]) > JND): areDifferent = True
	return areDifferent

## Log related method ------------------------------------------------

def print_OneLine(n): # len(msg_list[-1])
    sys.stdout.write('\r!!! ray(s) missed: {0}'.format(n))
    sys.stdout.flush()

## OSC reshaping related method --------------------------------------

def shapeFaceMsg(faceID,matID,pListVect): # string shapping (particularly for pListVect)
	pList_string = ''
	for vect in pListVect:
		vectRound = [round(elmt,2) for elmt in vect[:]]
		p_string = str(vectRound[:])
		p_string = p_string.replace('[','').replace(']','').replace(',','')
		pList_string = pList_string + ' ' + p_string
	osc_msg = '/face ' + str(faceID) + ' ' + matID +  ' ' + pList_string
	return osc_msg

def shapeSourceListenerMsg(header,ID,mat44): # string shapping (particularly for mat44)
	mat44_str = ''
	for elmt in mat44.col: mat44_str = mat44_str + str(elmt.to_tuple(2)[:]) # to tuple allows to round the Vector
	mat44_str = mat44_str.replace('(','').replace(')',' ').replace(',','')
	osc_msg = header + ' ' + ID + ' ' + mat44_str
	return osc_msg

def shapeOscInMsg_a(msg): # Markus osc input message shapping
# Format OUT -- update (/upd) msg
# msg = (pathID, order, (coord0), (coordN), dist, (abs))
# msg = (1,2,(0,0,0),(8,8,8), 0, (0,0,0,0,0,0,0,0,0))
# Format OUT -- listeners&sources (#bundle) msg
# msg = ((/flag, name, (coord)), (same), .. ,(same))
# msg = ('/listener', 'listener_0', (-10.0, 0.0, 1.66))
	# print (msg)
	if msg[0] in ['/upd','/in']:
		msg_out = (msg[0][1::], msg[2], msg[3], ([round(elmt,2) for elmt in msg[4:7]]), ([round(elmt,2) for elmt in msg[7:10]]), round(msg[10],2), ([round(elmt,2) for elmt in msg[11::]]))

	elif msg[0] == '#bundle':
		bundle = msg[2::]
		list_out = ['bundle']
		for i in range(0,len(bundle)):
			list_out.extend([[bundle[i][0], bundle[i][2], [round(elmt,2) for elmt in bundle[i][3::]]]])
		msg_out = tuple(list_out)
	else:
		if gl.dbg: print ('\n','!!!!!!!! NOT KNOWN OSC MESSAGE !!!!!!!!',msg[:],'\n')
		msg_out = msg

	return msg_out

def shapeOscInMsg_v(msg_str): # Virchor osc input message shapping
# Format OUT
# (state, ID, (coodStart), (coordEnd))
# ('on', 45, (2.06, 0.0, 1.67), (28.2, 0.0))

	msg_list = msg_str.split(' ')

	onOff = msg_list[0][6:9].replace(' ', '')
	ID = int(msg_list[1])
	# print ('####',msg_list,len(msg_list[-1]))
	if len(msg_list) == 8 and len(msg_list[-1]) >= 4:
		# print (msg_list)
		coord1, coord2 = tuple([round(float(elmt),2) for elmt in msg_list[2:5]]), tuple([round(float(elmt),2) for elmt in msg_list[5::]])
	else: coord1, coord2 = (), ()
		# restart_line()
	# except IndexError:
	# 	coord1, coord2 = (), ()


	return (onOff,ID,coord1,coord2)

## OSC communication related method -----------------------------------

def sendOscMsg(ip,host,header,msg = ''): # send OSC 'header msg' at host@ip
	client = OSC.OSCClient()
	osc_msg = OSC.OSCMessage()
	osc_msg.setAddress(header)
	osc_msg.append(msg)
	# gl.logs['out'].append(osc_msg) # record OSC logs

	try:
		client.sendto(osc_msg,(ip,host))
		if gl.dbg: print ('-- sent to ' + str(host) + '@' + ip + ' OSC msg: \n' + header + ' ', msg, '\n')
	except TypeError: print ('## no route to', host, ip, 'to send -', header.split(' ')[0]) # may occur in OSC.py if no route to host


def getOscSocket(ip,host): # initialise a socket at host@ip

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# eventually set socket buffer size (up speed for real-time)
	if gl.connect['buffer_size']:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, gl.connect['buffer_size'])
		if gl.dbg: print (' ##### \n You set the socket.SO_RCVBUF size to', gl.connect['buffer_size'], '--- you may drop unprocessed packets \n ')

	isConnected = False
	try:
		sock.bind((ip, host))
		sock.setblocking(0)
		sock.settimeout(gl.connect['socket_timeout'])
		isConnected = True
	except OSError as e:
		print ('###', e)
	return (sock, isConnected)

def readBuffer(): # read and decode socket content: print ('Received: ',osc_msg)

		# raw_msg = sock.recv(gl.connect['socket_size'])
		gl.lock.acquire()
		buff = copy.deepcopy(gl.connect['raw_msg'])
		gl.lock.release()
		if buff:
			if gl.connect['protocole'] == 'a':
				osc_msg = OSC.decodeOSC(buff)
				out_msg = shapeOscInMsg_a(osc_msg)
			elif gl.connect['protocole'] == 'v':
				osc_msg = buff.decode("utf-8")
				out_msg = shapeOscInMsg_v(osc_msg)
			if gl.dbg: print ('++ received from ', gl.connect['socket_' + gl.connect['protocole']].getsockname()[0] + ':' + str(gl.connect['socket_' + gl.connect['protocole']].getsockname()[1]), ': \n', out_msg )
			return out_msg
		# ''.join(total_data)
		else: return ()

def readSocket(sock):
		try:
			raw_msg = sock.recv(gl.connect['socket_size'])

			if raw_msg:

				if gl.connect['protocole'] == 'a':
					osc_msg = OSC.decodeOSC(raw_msg)
					# print ('processing \n', osc_msg)
					out_msg = shapeOscInMsg_a(osc_msg)
				elif gl.connect['protocole'] == 'v':
					osc_msg = raw_msg.decode("utf-8")
					out_msg = shapeOscInMsg_v(osc_msg)
				if gl.dbg: print ('++ received from ', gl.connect['socket_' + gl.connect['protocole']].getsockname()[0] + ':' + str(gl.connect['socket_' + gl.connect['protocole']].getsockname()[1]), ': \n', out_msg )
				# gl.logs['in'].append(out_msg) # record OSC logs
				return out_msg
			# ''.join(total_data)
			else: return ()

		except socket.timeout: # nothing received
			return ()
		except OSError: # socket closed
			return ()

def sockStreamIn(sock, size, lock):
	while True:
		try:
			# print ('-')
			# print (gl.connect['raw_msg'])

			buff = sock.recv(size)
			# print (buff)
			if buff:
				lock.acquire()
				gl.connect['raw_msg'] = buff
				lock.release()
				# print (buff)
		except socket.timeout: # nothing received
			pass
		except OSError: # socket closed
			pass

## OSC update (send) related method ------------------------------------------

def updateOSC_Rooms(objDict): # update room in EVERTims
	polygonDict = getRoomFacesAndMaterials(objDict['rooms'][0]) # [0] (static) since EVERTims doesn't handle multi-room scene
	for key in polygonDict.keys():
		faceID = str(key)
		matID = polygonDict[key]['material']
		p0123 = polygonDict[key]['vertices']
		msg = shapeFaceMsg(faceID,matID,p0123)
		sendOscMsg(gl.connect['ip_evert'],gl.connect['port_w'],msg)


def updateAllowed(mat1, mat2): # check timer and matPos difference to see if update allowed
	# Check TIME
	own = gl.getCurrentController().owner
	if  own['Timer'] == 0 or own['Timer'] > gl.update['jnd_time']: # first time or if update time constraint reached
		own['Timer'] = 0
		upd_timer = True
	else: upd_timer = False
	# Check POS/ORI
	upd_pos = areDifferent_Mat44(mat1, mat2, gl.update['jnd_mvmt'])
	return upd_pos and upd_timer

def updateOSC_Listeners(objDict, forceUpdate = False): # update listeners in EVERTims, forceUpdate flag enables forcing update
	for n in range(len(objDict['listeners'])):
		obj = objDict['listeners'][n]
		shallUpdate = updateAllowed(obj.worldTransform, objDict['listeners_oldMat44'][n])
		if forceUpdate or shallUpdate:
			osc_msg = shapeSourceListenerMsg('/listener', obj.name, obj.worldTransform)
			sendOscMsg(gl.connect['ip_evert'],gl.connect['port_w'],osc_msg)
			objDict['listeners_oldMat44'][n] = obj.worldTransform.copy()

def updateOSC_Sources(objDict, forceUpdate = False): # update sources pos in EVERTims
	for n in range(len(objDict['sources'])):
		obj = objDict['sources'][n]
		if forceUpdate or not obj.worldTransform == objDict['sources_oldMat44'][n]: # if you forced update or the object moved
			osc_msg = shapeSourceListenerMsg('/source', obj.name,obj.worldTransform)
			sendOscMsg(gl.connect['ip_evert'],gl.connect['port_w'],osc_msg)
			objDict['sources_oldMat44'][n] = obj.worldTransform.copy()

## OSC update (receive) related method ------------------------------------------

def syncPathDict(pathDict,msg_in): # A CORRIGER
# Format OUT
# msg = (1,2,(0,0,0),(8,8,8), 0, (0,0,0,0,0,0,0,0,0))
# msg = (pathID, order, (coord0), (coordN), dist, (abs))

	msg = msg_in[1::]
	isNewPath = False
	# print ('--')
	# for elmt in msg: print (elmt)
	# print ('--')
	if not msg[0] in pathDict:
		pathDict[msg[0]] = evertClass.Path(msg[0])
		isNewPath = True
	pathDict[msg[0]].setLine(msg[1], msg[2], msg[3], msg[5])
	pathDict[msg[0]].length = msg[4]
	pathDict[msg[0]].ID = msg[0]

	return isNewPath

def syncLineDict(lineDict,msg_in):
# Format OUT
# msg = (1,(0,0,0),(8,8,8))
# msg = (lineID, (coord1), (coord2))

	msg = msg_in[1::]
	isNewLine = False
 	# print ('--',msg, len(msg), len(msg[-1]))
	if len(msg) == 3 and len(msg[-1]) == 3: # if full received msg through OSC
		if not msg[0] in lineDict:
			lineDict[msg[0]] = evertClass.Line(msg[0],msg[1], msg[2])
			isNewLine = True
		else: lineDict[msg[0]].setCoord(msg[1], msg[2])
	else:
		if gl.dbg:
			gl.missedRay += 1
			print_OneLine(gl.missedRay)
			# print('.', end="")
			# sys.stdout.write('*')

	return isNewLine

## Scene harvesting related method ------------------------------------

def updateObjDict(scene,obj_to_update = ''): # update scene objects of EVERTims interest in objDict, obj_to_update, if defined, forbid update of other objects
	updateObjList = [key[:-1] for key in gl.objDict.keys()]
	for obj in scene.objects:
		for elmt in updateObjList:
			if elmt in obj: # if object has 'elmt' property
				if not obj_to_update:  # if not selective update
					gl.objDict[elmt +'s'].append(obj)
					if not elmt == 'room': gl.objDict[elmt + 's_oldMat44'].append(obj.worldTransform.copy())
				elif obj_to_update == elmt + 's': # selecive update
					gl.objDict[elmt + 's'].append(obj)
					if not elmt == 'room': gl.objDict[elmt + 's_oldMat44'].append(obj.worldTransform.copy())
	if gl.dbg:
		print ('- listeners: ', [elmt for elmt in gl.objDict['listeners']])
		print ('- sources: ', [elmt for elmt in gl.objDict['sources']])
		print ('- room: ', [elmt for elmt in gl.objDict['rooms']], '\n')

def getRoomFacesAndMaterials(room): # return room (faces / materials) dict
	polygonDict = {} 		  # a dict that holds faces (dict), their vertices (dict: positions and materials)
	mesh = room.meshes[0] 	  # WARNING: supposed to work with a single mesh material
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

		if gl.dbg: print ('  ' + 'face ' + str(n) + ' - materials '+ poly.material_name.replace('MA',''))

	return polygonDict

