from bge import logic as gl
import scripts.evertMethods as evertMethods
import scripts.evertClass as evertClass
import threading

def init(cont):

	# Update rooms / listeners / sources list
	evertMethods.updateObjDict(gl.getCurrentScene(),'') # update rooms, listener and sources, 2nd arg set selectivity

	if (gl.objDict['listeners'] and gl.objDict['sources'] and gl.objDict['rooms']): # if EVERTims isn't useless :)

		# OSC send initialisation messages
		evertMethods.updateOSC_Rooms(gl.objDict)
		evertMethods.updateOSC_Listeners(gl.objDict,True)
		evertMethods.updateOSC_Sources(gl.objDict,True)

		# OSC send '/facefinished' (start calculations) message
		evertMethods.sendOscMsg(gl.connect['ip_evert'],gl.connect['port_w'],'/facefinished')

	else: print ('\n ###### EVERTims WARNING: \n You should create at least 1 room, 1 listener and 1 source (check activated layers if already done) \n ######################## \n')

	if gl.connect['protocole']:

		# Init local socket (read from EVERTims)
		(gl.connect['socket_' + gl.connect['protocole']], isConnected) = evertMethods.getOscSocket(gl.connect['ip_local'],gl.connect['port_r_' + gl.connect['protocole']])

		if isConnected:
			print('### Listening to incoming packets from EVERT server')
			cont.owner['Init'] = True # start Main thread

			if gl.connect['buffer_size']:
				# Launch threading (socket read fast (simple) method)
				gl.lock = threading.Lock()
				gl.thread = threading.Thread(target=evertMethods.sockStreamIn, args=(gl.connect['socket_' + gl.connect['protocole']], gl.connect['socket_size'], gl.lock))
				gl.thread.setDaemon(True)
				gl.thread.start()

		else:
			print('### Cannot establish downlink connection to EVERT server')

	else: print ('### No EVERTims protocole selected - simple send mode started ### ')

def run(cont):

	# Update Source / Listener position in EVERTims
	evertMethods.updateOSC_Sources(gl.objDict)
	evertMethods.updateOSC_Listeners(gl.objDict)

	# Receive EVERTims OSC msg (Virchor or Auralization Protocol)
	if gl.connect['protocole'] == 'v': # Virchor protocol

		# RealTime / NoError Raytracing mode selection method
		if gl.connect['buffer_size']: evert_msg_v = evertMethods.readBuffer()
		else: evert_msg_v = evertMethods.readSocket(gl.connect['socket_' + gl.connect['protocole']])


		if evert_msg_v:
			if evert_msg_v[0] == 'on':
				isNewLine = evertMethods.syncLineDict(gl.lineDict,evert_msg_v)
				if isNewLine:
					gl.getCurrentScene().post_draw.append(gl.lineDict[evert_msg_v[1]].drawPath)
					gl.lineDict[evert_msg_v[1]].posInPost_draw = len(gl.getCurrentScene().post_draw) - 1 # update pos in post_draw list for latter removal
			elif evert_msg_v[0] == 'off':
				try:
					if gl.dbg: print ('removing line', gl.lineDict[evert_msg_v[1]].ID)
					gl.getCurrentScene().post_draw.pop(gl.lineDict[evert_msg_v[1]].posInPost_draw)
					for key in gl.lineDict.keys():
						if gl.lineDict[key].posInPost_draw > gl.lineDict[evert_msg_v[1]].posInPost_draw:
							gl.lineDict[key].posInPost_draw -= 1
					del (gl.lineDict[evert_msg_v[1]])
				except KeyError: pass # if /off msg sent at evertims start when not closed between 2 bge runs.
			if gl.dbg:
				print (len(gl.getCurrentScene().post_draw),'rays on screen \n')
				# for key in gl.lineDict.keys(): print (gl.lineDict[key].ID,gl.lineDict[key].posInPost_draw,gl.lineDict[key])
				# print ('#######','\n',gl.getCurrentScene().post_draw)

	elif gl.connect['protocole'] == 'a': # Auralization protocol

		# Receive EVERTims OSC msg
		if gl.connect['buffer_size']: evert_msg_a = evertMethods.readBuffer()
		else: evert_msg_a = evertMethods.readSocket(gl.connect['socket_' + gl.connect['protocole']])

		if evert_msg_a: # process evertims message

			if evert_msg_a[0] in ['upd','in']:
				isNewPath = evertMethods.syncPathDict(gl.pathDict,evert_msg_a) # newPath is True if path wasn't in gl.pathDict
				if gl.dbg: gl.pathDict[evert_msg_a[1]].printLines()

			else:
				if gl.dbg: print ('### non processed OSC msg: \n message: \n', evert_msg_a)
