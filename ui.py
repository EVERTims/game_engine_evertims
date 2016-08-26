import bpy
from bpy.types import Panel

# ############################################################
# User Interface
# ############################################################

class EVERTimsUIBase:
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_description= ""
    bl_category = "EVERTims"

class EVERTimsToolBar(EVERTimsUIBase, Panel):

    bl_label = "EVERTims"

    @staticmethod

    def draw_header(self, context):
        # Enable layout
        evertims = context.scene.evertims
        self.layout.prop(evertims, "enable_evertims", text="Enable Module")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        evertims = scene.evertims

        layout.enabled = evertims.enable_evertims

        # ----------------------------------------------

        # Import elements
        col = layout.column()
        col.label("Import elements:")
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Template scene", icon='MESH_CUBE').arg = 'scene'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Logic", icon='EMPTY_DATA').arg = 'logic'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Room & Materials", icon='MESH_CUBE').arg = 'room'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Source", icon='MESH_CUBE').arg = 'source'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Listener", icon='MESH_CUBE').arg = 'listener'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_script", text="Room materials (.txt)", icon='TEXT').arg = 'materialList'
        rowsub = col.row(align=True)
        rowsub.alignment = 'RIGHT'
        rowsub.label("> see Text Editor")

        # line break
        col = layout.column()

        # Define KX_GameObjects as EVERTims elements
        col = layout.column()
        col.label("Selected to EVERTims element:")
        rowsub = col.row(align=True)
        rowsub.operator("evert.set_evert_elmt", text="Room", icon='CONSTRAINT').arg = 'room'
        rowsub = col.row(align=True)
        rowsub.operator("evert.set_evert_elmt", text="Source", icon='CONSTRAINT').arg = 'source'
        rowsub = col.row(align=True)
        rowsub.operator("evert.set_evert_elmt", text="Listener", icon='CONSTRAINT').arg = 'listener'

        # line break
        col = layout.column()
        col.label("")

        # Network configuration
        col = layout.column()

        rowsub = col.row(align=True)
        rowsub.label("Local IP adress & port:")
        rowsub = col.row(align=True)
        split = rowsub.split(percentage=0.6)
        colsub = split.column()
        colsub.prop(evertims, "ip_local", text="")
        colsub = split.column()
        colsub.prop(evertims, "port_read", text="port")

        rowsub = col.row(align=True)
        rowsub.label("EVERTims IP adress & port:")
        rowsub = col.row(align=True)
        split = rowsub.split(percentage=0.6)
        colsub = split.column()
        colsub.prop(evertims, "ip_client", text="")
        colsub = split.column()
        colsub.prop(evertims, "port_write", text="port")

        rowsub = col.row(align=True)
        rowsub.label("Evert Sound Engine IP adress & port:")
        rowsub = col.row(align=True)
        split = rowsub.split(percentage=0.6)
        colsub = split.column()
        colsub.prop(evertims, "ip_sound_engine", text="")
        colsub = split.column()
        colsub.prop(evertims, "port_sound_engine", text="port")

        # line break
        col = layout.column()
        col.label("")

        # EVERTims auralization engine setup
        col = layout.column()
        col.label("Embedded auralization engine:")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "auralization_client_path_to_binary", text="exe")

        rowsub = col.row(align=True)
        if not evertims.enable_auralization_client:
            rowsub.operator("evert.evertims_auralization_client", text="START", icon="RADIOBUT_OFF").arg ='PLAY'
        else:
            rowsub.operator("evert.evertims_auralization_client", text="STOP", icon="REC").arg ='STOP'

        # line break
        col = layout.column()
        col.label("")

        # EVERTims raytracing client setup
        col = layout.column()
        col.label("Embedded raytracing client:")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "raytracing_client_path_to_binary", text="ims")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "raytracing_client_path_to_matFile", text="mat")

        rowsub = col.row(align=True)
        rowsub.label("Reflection order:")
        rowsub = col.row(align=True)
        split = rowsub.split(percentage=0.5)
        colsub = split.column()
        colsub.prop(evertims, "min_reflection_order", text="min")
        colsub = split.column()
        colsub.prop(evertims, "max_reflection_order", text="max")

        rowsub = col.row(align=True)
        rowsub.prop(evertims, "debug_logs_raytracing", text="print raytracing client logs in console")
        rowsub = col.row(align=True)
        if not evertims.enable_raytracing_client:
            rowsub.operator("evert.evertims_raytracing_client", text="START", icon="RADIOBUT_OFF").arg ='PLAY'
        else:
            rowsub.operator("evert.evertims_raytracing_client", text="STOP", icon="REC").arg ='STOP'

        # line break
        col = layout.column()
        col.label("")

        # Simulation Setup
        col = layout.column()
        # col.label("Simulation parameters:")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "debug_rays", text="draw rays in 3DView & BGE")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "debug_logs", text="print local logs in Blender console")
        rowsub = col.row(align=True)
        rowsub.label("Movement update threshold:")
        rowsub = col.row(align=True)
        split = rowsub.split(percentage=0.5)
        colsub = split.column()
        colsub.prop(evertims, "movement_threshold_loc", text="loc (m)")
        colsub = split.column()
        colsub.prop(evertims, "movement_threshold_rot", text="rot (deg)")

        # line break
        col = layout.column()

        # Auralization in BPY
        col = layout.column()
        col.label("On the fly auralization:")
        rowsub = col.row(align=True)
        if not evertims.enable_edit_mode:
            rowsub.operator("evert.evertims_in_edit_mode", text="START", icon="RADIOBUT_OFF").arg ='PLAY'
        else:
            rowsub.operator("evert.evertims_in_edit_mode", text="STOP", icon="REC").arg ='STOP'

        # Auralization in BGE (exact equivalent of pressing "P" over 3D view)
        col = layout.column()
        col.label("In-game auralization: simply launch BGE")


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(EVERTimsToolBar)

def unregister():
    bpy.utils.unregister_class(EVERTimsToolBar)
