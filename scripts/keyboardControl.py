from bge import logic as gl
from bge import events
import scripts.evertMethods as evertMethods
import time

def main(controller):
	# Get owner and curent scene
	owner = controller.owner
	scene = gl.getCurrentScene()

	# Map keyboard events
	active_events = gl.keyboard.active_events

	for key,status in active_events.items():
		print(key)
		# print ('keyID', key, 'key:', events.EventToString(key),'status', status)
		if key == 108 and status == 1: # add listener if 'l' pressed
			obj = scene.objectsInactive['Listener'] # object to add
			objRef = scene.objects['Logic'] # add it at 'Logic' KX_GameObject Position
		if key == 120 and status == 1: # add source if 'x' pressed
			obj = scene.objectsInactive['Source']
			objRef = scene.objects['Logic']
		if key == 32 and status == 1: # send facefinished if 'spacebar' is pressed
			evertMethods.sendOscMsg(gl.connect['ip'],gl.connect['port_w'],'/facefinished')
		if key == 109 and status == 1: # close sockets and quit if 'M' is pressed
			try:
				print ('## closing ' + gl.connect['socket_a'].getsockname()[0] + ':' + str(gl.connect['socket_a'].getsockname()[1]) + ' socket..')
				gl.connect['socket_a'].close()
				print ('## done')
			except KeyError: pass
			try:
				print ('## closing ' + gl.connect['socket_v'].getsockname()[0] + ':' + str(gl.connect['socket_v'].getsockname()[1]) + ' socket..')
				gl.connect['socket_v'].close()
				print ('## done')
			except KeyError: pass
			# print (gl.startTime*1e-9)
			total_time = round(10*(time.clock()-gl.startTime),1)
			print ('mean loss: {0} ray/sec ({1} rays / {2} secs)'.format(round(gl.missedRay/total_time,1),gl.missedRay, total_time))

			# record OSC logs
			# recordLogFile(gl.logs['out'], 'evertims_osc_log_out')
			# recordLogFile(gl.logs['in'], 'evertims_osc_log_in')

			# Quit bge
			controller.activate(owner.actuators['Quit'])
	try:
		scene.addObject(obj, objRef) # 3rd parm is existence time, default is 0 (infinite)
		print ('** added object:', obj, 'at position:', objRef.worldPosition)
	except UnboundLocalError: pass

def recordLogFile(recordList, recordName = 'evertims_osc_log', recordDir = gl.expandPath('//')):
    fileRecord = open(recordDir + '/' + recordName + '.txt', 'w')
    fileRecord.write(str(recordList))
    fileRecord.close()
    print ('recorded', recordName, 'at', recordDir)
