# print (__name__, 'started')
from . import evertClass
from . import OSC
from . import evertMain
from . import evertMethods

from bge import logic as gl
import time

# bge.logic parameters definition & configuration
gl.dbg = True    # print debug ouputs in console option (impact Raytracing real-time performances)

gl.update={
'jnd_mvmt': 0.2, # Just noticeable difference mouvement update (source / listener) towards EVERTims
'jnd_time': 0.2, # trigger time update (source / listener) towards EVERTims every .. seconds (prevail against jnd_mvmt yet doesn't update if object not moved)
}

gl.connect = {
'raw_msg': '',              # To be filled in threading, contains raw socket datas awaiting to be processed (faster to forbid Evertims msg jamming the socket)
'ip_evert': 'localhost', # IP of EVERTims' computer
'ip_local': 'localhost', # IP of Blender's computer
'port_w': 3858,             # Port to write in EVERTims
'port_r_a': 3860,           # Port to read from EVERTims (Markus protocole)
'port_r_v': 3862,           # Port to read from EVERTims (VirChor protocole)
'socket_size': 2*1024,      # Size of reader socket (a_min = 124, v_min = ..?)
'socket_timeout': 1e-5,     # Timeout of reader socket
'buffer_size': 0,           # Buffer size (socket buffer) process will discard packets to receive new ones - no packet discarded if 0 (RealTime / NoError mode)
'protocole' : 'v',          # ('a'/'v') Which protocole to read (instanciate socket & all) from EVERTims (Markus/Virchor protocole)
}

gl.objDict = {
'listeners' : [],          # KX_GameObj list of obj with 'listener' property in scene
'listeners_oldMat44' : [], # Mat44 list of listeners' old worldTransform
'sources' : [],            # KX_GameObj list of obj with 'source' property in scene
'sources_oldMat44' : [],   # Mat44 list of sources' old worldTransform
'rooms' : []               # KX_GameObj list of obj with 'room' property in scene
}

gl.startTime = time.clock() # For profiling
gl.missedRay = 0 # dismissed rays counter

gl.pathDict = {}  # Path dictionnary instanciation (Receive Auralization protocol)
gl.lineDict = {}  # Line and Line dictionnary instanciation (Receive and Raytracing Virchor protocol)

# TO RECORD OSC Logs:
# uncomment the gl.logs['..'].append(..) in
# evertMethods.sendOscMsg and evertMethods.readSocket,
# the 2 "recordLogFile" lines in keyboardControl.py,
# and:
# gl.logs={
# 'in': [], # record logs OSC EVERTims -> Blender
# 'out': [], # record logs OSC Blender -> EVERTims
# }
