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
        obj = context.object

        layout.enabled = evertims.enable_evertims

        # ----------------------------------------------

        # Import elements
        col = layout.column()
        col.label("Import elements:")
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Template scene").arg = 'scene'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Logic").arg = 'logic'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Room").arg = 'room'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Source").arg = 'source'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_template", text="Listener").arg = 'listener'
        rowsub = col.row(align=True)
        rowsub.operator("evert.import_script", text="Room materials (.txt)").arg = 'materialList'
        rowsub = col.row(align=True)
        rowsub.alignment = 'RIGHT'
        rowsub.label("> see Text Editor")

        # Define elements
        col = layout.column()
        col.label("Selected to EVERTims element:")
        rowsub = col.row(align=True)
        rowsub.operator("evert.set_evert_elmt", text="Room").arg = 'room'
        rowsub = col.row(align=True)
        rowsub.operator("evert.set_evert_elmt", text="Source").arg = 'source'
        rowsub = col.row(align=True)
        rowsub.operator("evert.set_evert_elmt", text="Listener").arg = 'listener'

        # line break
        col = layout.column()
        col.label("")

        # Network configuration
        col = layout.column()
        rowsub = col.row(align=True)
        rowsub.label("Local IP address:")
        rowsub = col.row()
        rowsub.prop(evertims, "ip_local", text="")
        rowsub = col.row()
        rowsub.label("Port:")
        rowsub.prop(evertims, "port_read", text="")
        rowsub = col.row(align=True)
        rowsub.label("EVERTims IP address:")
        rowsub = col.row()
        rowsub.prop(evertims, "ip_client", text="")
        rowsub = col.row()
        rowsub.label("Port:")
        rowsub.prop(evertims, "port_write", text="")

        # line break
        col = layout.column()
        col.label("")

        # Simulation Setup
        col = layout.column()
        col.label("Simulation parameters:")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "debug_rays", text="Draw rays in BGE")
        rowsub = col.row(align=True)
        rowsub.prop(evertims, "debug_logs", text="Print BGE logs in console")
        rowsub = col.row(align=True)
        split = rowsub.split(percentage=0.7)
        colsub = split.column()
        colsub.label("Movement Sensitivity:")
        split = split.split()
        colsub = split.column()
        colsub.prop(evertims, "movement_jnd", text="")


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(EVERTimsToolBar)

def unregister():
    bpy.utils.unregister_class(EVERTimsToolBar)
