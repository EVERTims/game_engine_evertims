import bpy
import os
from bpy.types import Operator

 # to launch EVERTims raytracing client
import subprocess
# ---------------------------------------------------------------
# import components necessary to report EVERTims raytracing client
# logs in console
import sys
import threading
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names
# ---------------------------------------------------------------
# ADD PATHS (to evertims python module and asset file)
ASSET_FILE_NAME = "evertims-assets.blend"

def init_evertims_module_path(self, context):
    # get addon path
    current_script_file = os.path.realpath(__file__)
    current_script_directory = os.path.dirname(current_script_file)
    addon_path = os.path.join(current_script_directory, 'assets', 'scripts')

    # get logic object
    obj = context.scene.objects.get('Logic_EVERTims')
    obj.game.properties['evertims_path'].value = addon_path

# ---------------------------------------------------------------
# EXACT REPEAT OF SCRIPT IN __INIT__.PY UNTIL FOUND A CLEANER WAY
ignore_change_props_list = (
    "debug_logs_raytracing", "enable_raytracing_client",
    "raytracing_client_path_to_binary", "raytracing_client_path_to_matFile",
    "debug_logs_raytracing",
    "ip_sound_engine", "port_sound_engine",
    "enable_auralization_client", "auralization_client_path_to_binary",
    "min_reflection_order", "max_reflection_order",
    "enable_edit_mode", "rna_type", "screen_setup", "name", "bl_rna",
    "__dict__", "__doc__", "__module__", "__weakref__"
)


def update_evertims_props(self, context):
    scene = context.scene
    evertims = scene.evertims

    # remember current active object
    old_obj = bpy.context.scene.objects.active

    # get logic object
    obj = bpy.context.scene.objects.get('Logic_EVERTims')

    if obj:
        bpy.context.scene.objects.active = obj

        # sync. properties (for bge access) with GUI's
        for propName in dir(evertims):
            if not propName in ignore_change_props_list:
                propValue = eval('evertims.' + propName)
                obj.game.properties[propName].value = propValue

    # reset old active object
    bpy.context.scene.objects.active = old_obj
# ---------------------------------------------------------------

class EVERTimsImportObject(Operator):
    """Import default EVERTims element (KX_GameObject) into scene"""
    bl_label = "Import an object (KX_GameObject, Empty, etc.) from anther .blend file"
    bl_idname = 'evert.import_template'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    def execute(self, context):

        loadType = self.arg

        # cancel if simulation is running
        if context.scene.evertims.enable_edit_mode:
            self.report({'WARNING'}, 'Cannot import element while simulation is running')
            return {'CANCELLED'}

        # cleanup before we start
        bpy.ops.object.select_all(action='DESELECT')

        # set asset .blend file name
        filename = ASSET_FILE_NAME
        obj = None

        if loadType == 'scene':
            obj = self.loadAsset(filename, ('Logic_EVERTims', 'Room', 'Source', 'Listener_Rotate', 'Listener'))

        if loadType == 'logic':
            obj = self.loadAsset(filename, ('Logic_EVERTims'))


        if loadType == 'room':
            obj = self.loadAsset(filename, ('Room'))

        if loadType == 'source':
            obj = self.loadAsset(filename, ('Source'))

        if loadType == 'listener':
            obj = self.loadAsset(filename, ('Listener_Rotate', 'Listener'))

        if not obj:
            self.report({'ERROR'}, 'something went wrong')
            return {'CANCELLED'}
        else:

            obj.select = True
            bpy.context.scene.objects.active = obj
            # update logic object props if need be (to propagates GUI props to BGE props)
            if loadType == 'logic' or loadType == 'scene':
                update_evertims_props(self, context)
                init_evertims_module_path(self, context)
            return {'FINISHED'}

    def loadAsset(self, filename, objList):

        scriptPath = os.path.realpath(__file__)
        assetPath = os.path.join(os.path.dirname(scriptPath), 'assets', filename)

        try:
            with bpy.data.libraries.load(assetPath) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name in objList]

        except:
            return 'Asset file not found'

        for obj in data_to.objects:
            bpy.context.scene.objects.link(obj)

        return obj


class EVERTimsImportText(Operator):
    """Import the list of available EVERTims acoustic materials as a text file"""
    bl_label = "Import a text file from anther .blend file"
    bl_idname = 'evert.import_script'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    def execute(self, context):

        loadType = self.arg

        # set asset .blend file name
        filename = ASSET_FILE_NAME

        if loadType == 'materialList':
            isLoaded = self.loadAsset(filename, ('evertims-materials.txt'))

        if not isLoaded:
            self.report({'ERROR'}, 'something went wrong')
            return {'CANCELLED'}

        else:
            self.report({'INFO'}, 'EVERTims material file imported in Text Editor window.')
            return {'FINISHED'}

    def loadAsset(self, filename, objList):

        scriptPath = os.path.realpath(__file__)
        assetPath = os.path.join(os.path.dirname(scriptPath), 'assets', filename)

        try:
            with bpy.data.libraries.load(assetPath) as (data_from, data_to):
                data_to.texts = [name for name in data_from.texts if name in objList]
        except:
            return False

        return True


class EVERTimsSetObject(Operator):
    """Define currently selected object (KX_GameObject) as an EVERTims element"""
    bl_label = "Define a Blender object as an EVERTims element"
    bl_idname = 'evert.set_evert_elmt'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    def execute(self, context):

        loadType = self.arg

        # cancel if simulation is running
        if context.scene.evertims.enable_edit_mode:
            self.report({'WARNING'}, 'Cannot set element while simulation is running')
            return {'CANCELLED'}

        # get active object
        obj = bpy.context.scene.objects.active

        if not obj:
            self.report({'ERROR'}, 'select an object')
            return {'CANCELLED'}

        else:
            # get next available prop value (e.g. listener / source index)
            occupiedValues = []
            listOfobjWithSameProp = self.getListOfObjectsWithPropValue(loadType)
            for objTmp in listOfobjWithSameProp:
                occupiedValues.append(objTmp.game.properties[loadType].value)
            newPropValue = self.getNextAvailableInteger(occupiedValues)

            # prior to creation: remove eventual other elmt in scene: all
            # (evertims only handles single room / listener / source at the moment)
            # could be implemented in a simpler fashion, yet that way code's ready for:
            # - room / logic being limited to single instance
            # - listener / source auto numbering
            if newPropValue > 1:
                self.report({'INFO'}, 'Old EVERTims room will be replaced by selected one')
                for objTmp in listOfobjWithSameProp:
                    self.removeGamePropFromObj(objTmp, loadType)
                    newPropValue = 1

            # add property to object, designating it as evertims element
            bpy.ops.object.game_property_new(type='INT', name=loadType)
            obj.game.properties[loadType].value = newPropValue

            # update logic object props if need be (to propagates GUI props to BGE props)
            if (loadType == 'logic'): 
                update_evertims_props(self, context)
                init_evertims_module_path(self, context)

            return {'FINISHED'}

    def getListOfObjectsWithPropValue(self, propValue):
        """
        roam scene to check for KX_GameObjects with game logic propVvalue
        """
        objList = []
        for obj in bpy.context.scene.objects:
            if propValue in obj.game.properties:
                objList.append(obj)
        return objList

    def getNextAvailableInteger(self, integerList):
        """
        roam list of integer, returns the first non-present
        (starting from 1)
        """
        newVal = 1
        if not integerList:
            return 1
        else:
            for i in range(max(integerList)+1):
                index = i + 1
                if index not in integerList:
                    newVal = index
                    break
        return newVal

    def removeGamePropFromObj(self, obj, propName):
        """
        remove game logic property from object
        """
        # remember current active object
        old_obj = bpy.context.scene.objects.active
        # select object to get access to props editing
        bpy.context.scene.objects.active = obj
        # get prop index
        idx = obj.game.properties.find(propName)
        # remove property
        if idx > -1:
            bpy.ops.object.game_property_remove(idx)
        # reset old selected object
        bpy.context.scene.objects.active = old_obj

class EVERTimsInEditMode(Operator):
    """Start OSC sync. with EVERTims raytracing client. 
    Continuous upload of scene info (room, listener, etc.) for auralization and
    download of raytracing results for visual feedback."""
    bl_label = "Enable Blender to EVERTims raytracing client connection in edit mode (as opposed to BGE mode)"
    bl_idname = 'evert.evertims_in_edit_mode'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    from .assets.scripts.evertims import Evertims
    _evertims = Evertims()

    @staticmethod
    def handle_add(self, context):
        # EVERTimsInEditMode._handle_draw_callback = bpy.types.SpaceView3D.draw_handler_add(EVERTimsInEditMode._draw_callback, (self,context), 'WINDOW', 'PRE_VIEW')
        context.window_manager.modal_handler_add(self)
        EVERTimsInEditMode._handle_timer = context.window_manager.event_timer_add(0.075, context.window)
        if context.scene.evertims.debug_logs: print('added evertims callback to draw_handler')

    @staticmethod
    def handle_remove(context):
        if EVERTimsInEditMode._handle_timer is not None:
            context.window_manager.event_timer_remove(EVERTimsInEditMode._handle_timer)
            EVERTimsInEditMode._handle_timer = None
            # context.window_manager.modal_handler_add(self)
            # bpy.types.SpaceView3D.draw_handler_remove(EVERTimsInEditMode._handle_draw_callback, 'WINDOW')
            # EVERTimsInEditMode._handle_draw_callback = None
            if context.scene.evertims.debug_logs: print('removed evertims callback from draw_handler')

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def invoke(self, context, event):

        scene = context.scene
        evertims = scene.evertims
        loadType = self.arg

        # get active object
        # obj = bpy.context.scene.objects.active

        if loadType == 'PLAY':

            # init evertims
            isInitOk = self.initEvertims(context)

            if isInitOk:
                # update enable flag
                evertims.enable_edit_mode = True

                # add callback
                self.handle_add(self,context)

                return {'RUNNING_MODAL'}
            else:

                self.report({'ERROR'}, 'Create at least 1 room (with material), 1 listener, 1 source and import EVERTims Logic object')
                return {'CANCELLED'}


        elif loadType == 'STOP':
            # update enable flag
            evertims.enable_edit_mode = False

            # erase rays from screen
            context.area.tag_redraw()

            return {'CANCELLED'}


    def modal(self, context, event):
        """
        modal method, run always, call cancel function when Blender quit / load new scene
        """
        # kill modal
        if not context.scene.evertims.enable_edit_mode:
            self.cancel(context)

            # return flag to notify callback managet this callback no longer runs
            return {'CANCELLED'}

        # execute modal
        elif event.type == 'TIMER':
            # run evertims internal callbacks
            self._evertims.bpy_modal()
            # force bgl rays redraw (else only redraw rays on user input event)
            if not context.area is None:
                context.area.tag_redraw()

        return {'PASS_THROUGH'}


    def cancel(self, context):
        """
        called when Blender quit / load new scene. Remove local callback from stack
        """
        # remove local callback
        self.handle_remove(context)
        
        # remove nested callback
        self._evertims.handle_remove()

        # erase rays from screen
        if not context.area is None: 
            context.area.tag_redraw()


    def initEvertims(self, context):
        """
        init the Evertims() class instance, using GUI defined parameters (in EVERTims add-on pannel)
        """
        evertims = context.scene.evertims

        IP_EVERT = evertims.ip_client # EVERTims client IP address
        PORT_W = evertims.port_write # port used by EVERTims client to read data sent by the BGE
        IP_LOCAL = evertims.ip_local # local host (this computer) IP address, running the BGE
        PORT_R = evertims.port_read # port used by the BGE to read data sent by the EVERTims client
        DEBUG_LOG = evertims.debug_logs # enable / disable console log
        DEBUG_RAYS = evertims.debug_rays # enable / disable visual feedback on traced rays
        MOVE_UPDATE_THRESHOLD_VALUE_LOC = evertims.movement_threshold_loc # minimum value a listener / source must move to be updated on EVERTims client (m)
        MOVE_UPDATE_THRESHOLD_VALUE_ROT = evertims.movement_threshold_rot # minimum value a listener / source must rotate to be updated on EVERTims client (deg)

        # set debug mode
        self._evertims.setDebugMode(DEBUG_LOG)

        # self._evertims.setBufferSize(4096)

        # define EVERTs elements: room, listener and source
        # 1. reset local dicts if already filled 
        self._evertims.resetObjDict() 
        # (in case something changed, don't want to keep old evertims elmt instances)
        # 2. define new elements
        for obj in bpy.context.scene.objects:
            if 'room' in obj.game.properties:
                self._evertims.addRoom(obj)
                if evertims.debug_logs: print('adding room: ', obj.name)
            if 'source' in obj.game.properties:
                self._evertims.addSource(obj)
                if evertims.debug_logs: print('adding source: ', obj.name)
            if 'listener' in obj.game.properties:
                self._evertims.addListener(obj)
                if evertims.debug_logs: print('adding listener: ', obj.name)

        # get logic object
        logic_obj = bpy.context.scene.objects.get('Logic_EVERTims')

        # get room for later check
        room_obj = self._evertims.getRoom()

        # limit listener / source position updates in EVERTims Client
        self._evertims.setMovementUpdateThreshold(MOVE_UPDATE_THRESHOLD_VALUE_LOC, MOVE_UPDATE_THRESHOLD_VALUE_ROT)

        # init newtork connections
        self._evertims.initConnection_write(IP_EVERT, PORT_W)
        self._evertims.initConnection_read(IP_LOCAL, PORT_R)

        # activate raytracing
        self._evertims.activateRayTracingFeedback(DEBUG_RAYS)

        # check if evertims module is ready to start
        # print (self._evertims.isReady(), logic_obj, room_obj.material_slots)
        if self._evertims.isReady() and logic_obj:
            # print('isready', [e for e in room_obj.material_slots])
            if room_obj.material_slots:
                # print('2')
                # start EVERTims client
                if evertims.debug_logs: print ('start simulation...')
                # print('3')
                self._evertims.startClientSimulation()
                # print('4')
                return True


        print ('\n###### EVERTims SIMULATION ABORTED ###### \nYou should create at least 1 room (with an EVERTims material), 1 listener, 1 source, \nimport the EVERTims Logic object \nand define EVERTims client parameters.\n')
        return False


class EVERTimsRaytracingClient(Operator):
    """Start the Evertims raytracing client as a subprocess"""
    bl_label = "Start / Stop the EVERTims raytracing client from Blender GUI"
    bl_idname = 'evert.evertims_raytracing_client'
    bl_options = {'REGISTER', 'UNDO'}

    _raytracing_process = None
    _raytracing_debug_log_thread = None
    _raytracing_debug_log_queue = None
    _handle_timer = None
    _raytracing_debug_thread_stop_event = None

    arg = bpy.props.StringProperty()

    @staticmethod
    def handle_add(self, context):
        """
        called when starting the EVERTims raytracing client with debug mode enabled,
        starts necessary callbacks to output client logs in Blender console.
        """
        # start thread for non-blocking log
        EVERTimsRaytracingClient._raytracing_debug_log_queue = Queue()
        EVERTimsRaytracingClient._raytracing_debug_thread_stop_event = threading.Event() # used to stop the thread
        EVERTimsRaytracingClient._raytracing_debug_log_thread = threading.Thread(target=self.enqueue_output, args=(self._raytracing_process.stdout, EVERTimsRaytracingClient._raytracing_debug_log_queue, EVERTimsRaytracingClient._raytracing_debug_thread_stop_event))
        EVERTimsRaytracingClient._raytracing_debug_log_thread.daemon = True # thread dies with the program
        EVERTimsRaytracingClient._raytracing_debug_log_thread.start()

        # start modal
        context.window_manager.modal_handler_add(self)
        EVERTimsRaytracingClient._handle_timer = context.window_manager.event_timer_add(0.075,  context.window)
        if context.scene.evertims.debug_logs: print('added evertims raytracing log callback to draw_handler')

    @staticmethod
    def handle_remove(context):
        """
        called when terminating the EVERTims raytracing client with debug mode enabled,
        remove callbacks added in handle_add method.
        """
        if EVERTimsRaytracingClient._handle_timer is not None:
            # kill modal
            context.window_manager.event_timer_remove(EVERTimsRaytracingClient._handle_timer)
            EVERTimsRaytracingClient._handle_timer = None
            # context.window_manager.modal_handler_add(self)
        # indicate it's ok to finish log in stdout thread
        # EVERTimsRaytracingClient._raytracing_debug_log_thread.daemon = False
        EVERTimsRaytracingClient._raytracing_debug_thread_stop_event.set()
        if context.scene.evertims.debug_logs_raytracing:
            print('removed raytracing client log callback from modal stack')

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def enqueue_output(self, out, queue, stop_event):
        """
        Based on the Queue python module, this callback runs when debug mode enabled,
        allowing non-blocking print of EVERTims raytracing client logs in Blender console.
        """
        if not stop_event.is_set():
            for line in iter(out.readline, b''):
                queue.put(line)
            out.close()
        else:
            EVERTimsRaytracingClient._raytracing_debug_log_thread.stop()
            if evertims.debug_logs_raytracing:
                print('removed raytracing client log callback from modal stack')

    def invoke(self, context, event):
        """
        Method called when button attached to local bl_idname clicked
        """
        evertims = context.scene.evertims
        loadType = self.arg

        # start Evertims raytracing client (subprocess)
        if loadType == 'PLAY':


            # get launch command out of GUI properties
            # cmd = "/Users/.../evertims/bin/ims -s 3858 -a 'listener_1/127.0.0.1:3860' -v 'listener_1/localhost:3862' -d 1 -D 2 -m /Users/.../evertims/resources/materials.dat -p 'listener_1/'"
            client_cmd  = bpy.path.abspath(evertims.raytracing_client_path_to_binary)
            client_cmd += " -s " + str(evertims.port_write) # reader port
            client_cmd += " -a " + "listener_1" + "/" + evertims.ip_sound_engine + ":" + str(evertims.port_sound_engine)
            client_cmd += " -v " + "listener_1" + "/" + evertims.ip_local + ":" + str(evertims.port_read)
            client_cmd += " -d " + str(evertims.min_reflection_order)
            client_cmd += " -D " + str(evertims.max_reflection_order)
            client_cmd += " -p " + "listener_1/ "
            client_cmd += " -m " + bpy.path.abspath(evertims.raytracing_client_path_to_matFile)


            # launch subprocess
            EVERTimsRaytracingClient._raytracing_process = subprocess.Popen(client_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, close_fds=ON_POSIX)
            evertims.enable_raytracing_client = True

            # enable log in Blender console if debug mode enabled
            if evertims.debug_logs_raytracing:
                print('launch EVERTims raytracing client subprocess')
                print('command: \n', client_cmd)
                self.handle_add(self, context)
                return {'RUNNING_MODAL'}

            else:
                return {'FINISHED'}

        # terminate Evertims raytracing client (subprocess)
        elif loadType == 'STOP':

            # terminate subprocess
            if self._raytracing_process: # if process has been (e.g. manually) closed since
                self._raytracing_process.terminate()
            evertims.enable_raytracing_client = False

            # terminate log-in-Blender-console related thread if debug mode enabled
            if evertims.debug_logs_raytracing or self._handle_timer: # (if debug flag disabled while running)
                print('terminate EVERTims raytracing client subprocess')
                self.handle_remove(context)

            return {'CANCELLED'}


    def modal(self, context, event):
        """
        modal method, run always, call cancel function when Blender quit / load new scene
        """

        if event.type == 'TIMER':
            try:
                # get line from non-blocking Queue, attached to debug-log thread
                line = EVERTimsRaytracingClient._raytracing_debug_log_queue.get_nowait() # or q.get(timeout=.1)
            except Empty: # no output to print yet
                pass
            else: # got line, ready to print
                sys.stdout.write(line.decode('utf-8'))

        return {'PASS_THROUGH'}


    def cancel(self, context):
        """
        function called when Blender quit / load new scene. Remove local callback from stack
        """
        self.handle_remove(context)


class EVERTimsAuralizationClient(Operator):
    """Start the EVERTims auralization client as a subprocess"""
    bl_label = "Start / Stop the EVERTims auralization client from Blender GUI"
    bl_idname = 'evert.evertims_auralization_client'
    bl_options = {'REGISTER', 'UNDO'}

    _process = None

    arg = bpy.props.StringProperty()

    def invoke(self, context, event):
        """
        Method called when button attached to local bl_idname clicked
        """
        evertims = context.scene.evertims
        loadType = self.arg

        # start Evertims auralization client (subprocess)
        if loadType == 'PLAY':

            # get launch command out of GUI properties
            client_cmd  = bpy.path.abspath(evertims.auralization_client_path_to_binary)

            # launch subprocess
            EVERTimsAuralizationClient._process = subprocess.Popen(client_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, close_fds=ON_POSIX)
            evertims.enable_auralization_client = True

            return {'FINISHED'}

        # terminate Evertims raytracing client (subprocess)
        elif loadType == 'STOP':

            # terminate subprocess
            if self._process: # if process has been (e.g. manually) closed since
                self._process.terminate()
            evertims.enable_auralization_client = False

            return {'CANCELLED'}


# ############################################################
# Un/Registration
# ############################################################

classes = (
    EVERTimsImportObject,
    EVERTimsImportText,
    EVERTimsSetObject,
    EVERTimsInEditMode,
    EVERTimsRaytracingClient,
    EVERTimsAuralizationClient
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
