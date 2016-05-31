import bpy
import os
from bpy.types import Operator

# ---------------------------------------------------------------
# EXACT REPEAT OF SCRIPT IN __INIT__.PY UNTIL FOUND A CLEANER WAY
ignore_change_props_list = (
    "rna_type", "screen_setup", "name", "bl_rna",
    "__dict__", "__doc__", "__module__", "__weakref__"
)

def update_evertims_props(self, context):
    scene = context.scene
    evertims = scene.evertims

    # get logic object
    obj = bpy.context.scene.objects.get('Logic_EVERTims')

    if obj:
        bpy.context.scene.objects.active = obj

        # sync. properties (for bge access) with GUI's
        for propName in dir(evertims):
            if not propName in ignore_change_props_list:
                propValue = eval('evertims.' + propName)
                obj.game.properties[propName].value = propValue
# ---------------------------------------------------------------

class EVERTimsImportElements(Operator):
    """"""
    bl_label = "Load Configuration File"
    bl_idname = 'evert.import_template'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    def execute(self, context):

        loadType = self.arg

        # cleanup before we start
        bpy.ops.object.select_all(action='DESELECT')

        # set asset .blend file name
        filename = 'evertims-assets.blend'
        obj = None

        if loadType == 'scene':
            obj = self.loadAsset(filename, ('Logic_EVERTims', 'Room', 'Source', 'Listener_Rotate', 'Listener'))

        if loadType == 'logic':
            obj = self.loadAsset(filename, ('Logic_EVERTims'))


        if loadType == 'room':
            obj = self.loadAsset(filename, ('Room'))

        if loadType == 'source':
            print('import source')
            obj = self.loadAsset(filename, ('Source'))

        if loadType == 'listener':
            obj = self.loadAsset(filename, ('Listener_Rotate', 'Listener'))

        if not obj:
            self.report({'ERROR'}, 'something went wrong')
            return {'CANCELLED'}
        else:

            obj.select = True
            bpy.context.scene.objects.active = obj
            update_evertims_props(self, context)
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


class EVERTimsSetElements(Operator):
    """"""
    bl_label = "Load Configuration File"
    bl_idname = 'evert.set_evert_elmt'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    def execute(self, context):

        loadType = self.arg

        # get active object
        obj = bpy.context.scene.objects.active

        if not obj:
            self.report({'ERROR'}, 'select an object')
            return {'CANCELLED'}

        else:
            bpy.ops.object.game_property_new(type='INT', name=loadType)
            prop = obj.game.properties[loadType]
            prop.value = 0
            return {'FINISHED'}

class EVERTimsPopupMaterial(Operator):
    """"""
    bl_label = "Load Configuration File"
    bl_idname = 'evert.pop_up_materials'
    bl_options = {'REGISTER', 'UNDO'}

    arg = bpy.props.StringProperty()

    def execute(self, context):

        loadType = self.arg
        return {'FINISHED'}




# class EVERTimsLauncher(bpy.types.Operator):
#     """"""
#     bl_label = "EVERTims Launcher"
#     bl_idname = 'evert.launcher'
#     bl_options = {'REGISTER', 'UNDO'}

#     arg = bpy.props.StringProperty(options={'HIDDEN'})

#     def execute(self, context):

#         # arg = self.arg.split('.')
#         arg = self.arg

#         # get file path
#         scene = context.scene
#         evertims = scene.evertims

#         if arg == 'start':
#             # tryout, start blenderplayer
#             # bpy.ops.wm.blenderplayer_start()

#             import subprocess
#             args = ['python3', '/Users/AstrApple/WorkSpace/Blender_Workspace/addons/blendervr/source/blenderVR', 'controller']
#             evertims.proc = subprocess.Popen(args,stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
#             print('opened',evertims.proc)

#             # outs, errs = evertims.proc.communicate(timeout=15)
#             outs, errs = evertims.proc.communicate()
#             print('first words: \n', outs,errs)

#             return {'FINISHED'}

#         elif arg == 'stop':
#             evertims.proc.kill()
#             outs, errs = evertims.proc.communicate()
#             print('subprocess killed, last words:')
#             print(outs,errs)

#             return {'FINISHED'}
#         elif arg == 'debug.window':
#             print('open debug window')
#             area = bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
#             context.area.type = 'CONSOLE'
#             # bpy.ops.screen.new('INVOKE_DEFAULT')


#             return {'FINISHED'}

#         else:
#             self.report({'ERROR'}, 'arg (in launcher) not defined yet')
#             return {'CANCELLED'}


# ############################################################
# Un/Registration
# ############################################################

classes = (
    # EVERTimsLoadConfigurationFile,
    EVERTimsImportElements,
    EVERTimsSetElements,
    EVERTimsPopupMaterial,
    # EVERTimsLauncher
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
