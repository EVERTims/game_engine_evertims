#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

bl_info = {
    "name": "EVERTims, real-time auralization framework",
    "author": "David Poirier-Quinot",
    "version": (0, 1),
    "blender": (2, 7, 8),
    "location": "3D View > Toolbox",
    "description": "A collection of tools to configure your EVERTims environment.",
    "warning": "",
    'tracker_url': "https://evertims.github.io/website/#contact",
    "wiki_url": "https://evertims.github.io/website",
    'support': 'COMMUNITY',
    "category": "Game Engine"
}

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
else:
    import bpy
    import os
    from bpy.props import (
            StringProperty,
            EnumProperty,
            BoolProperty,
            IntProperty,
            FloatProperty,
            PointerProperty
            )
    from bpy.types import (
            PropertyGroup,
            AddonPreferences
            )
    from . import (
            ui,
            operators
            )
import imp


# ---------------------------------------------------------------
# EXACT REPEAT OF SCRIPT IN __INIT__.PY UNTIL FOUND A CLEANER WAY
ignore_change_props_list = (
    "debug_logs_raytracing", "enable_raytracing_client",
    "debug_logs_raytracing",
    "ip_sound_engine", "port_sound_engine",
    "enable_auralization_client",
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
    if old_obj:
        bpy.context.scene.objects.active = old_obj
# ---------------------------------------------------------------

class EVERTimsSettings(PropertyGroup):

    enable_evertims = BoolProperty(
            name="Enable EVERTims",
            description='Activate EVERTims module in BGE',
            default=True,
            update=update_evertims_props
            )
    enable_edit_mode = BoolProperty(
            name="Enable EVERTims in EDIT mode",
            description='Activate real-time update of the EVERTims client from Blender outside the BGE (in casual edit mode)',
            default=False,
            )
    debug_logs_raytracing = BoolProperty(
            name="Print Raytracing Logs",
            description='Print raytracing client logs in Blender console',
            default=False,
            )
    debug_rays = BoolProperty(
            name="Draw Rays",
            description='Enable visual feedback on EVERTims ratracing in Blender',
            default=True,
            update=update_evertims_props
            )
    debug_logs = BoolProperty(
            name="Print Logs",
            description='Print logs of the EVERTims python module in Blender console',
            default=False,
            update=update_evertims_props
            )
    movement_threshold_loc = FloatProperty(
            name="Movement threshold location",
            description="Minimum value a listener / source must move to be updated on EVERTims client",
            default=1.0,
            )
    movement_threshold_rot = FloatProperty(
            name="Movement threshold rotation",
            description="Minimum value a listener / source must rotate to be updated on EVERTims client",
            default=5.0,
            update=update_evertims_props
            )
    ip_local = StringProperty(
            name="IP local",
            description="IP of the computer running Blender",
            default="127.0.0.1", maxlen=1024,
            update=update_evertims_props
            )
    ip_client = StringProperty(
            name="IP EVERTims client",
            description="IP of the computer running the EVERTims raytracing client",
            default="127.0.0.1", maxlen=1024,
            update=update_evertims_props
            )
    port_write = IntProperty(
            name="Port write",
            description="Port used by EVERTims raytracing client to read data sent by the Blender",
            default=3858,
            update=update_evertims_props
            )
    port_read = IntProperty(
            name="Port read",
            description="Port used by Blender to read data sent by the EVERTims raytracing client",
            default=3862,
            update=update_evertims_props
            )

    # EVERTims Raytracing client properties
    enable_raytracing_client = BoolProperty(
            name="Launch EVERTims raytracing client",
            description='Launch the EVERTims raytracing client as a subprocess (embedded in Blender)',
            default=False,
            )
    ip_sound_engine = StringProperty(
            name="IP EVERTims auralization client",
            description="IP of the computer running the EVERTims auralization client",
            default="127.0.0.1", maxlen=1024,
            )
    port_sound_engine = IntProperty(
            name="Port EVERTims auralization client",
            description="Port used by the auralization client to read data sent by the raytracing client",
            default=3860,
            )
    min_reflection_order = IntProperty(
            name="Min reflection order",
            description="Min reflection order passed to the embedded EVERTims client",
            default=1,
            )
    max_reflection_order = IntProperty(
            name="Max reflection order",
            description="Max reflection order passed to the embedded EVERTims client",
            default=2,
            )

    # EVERTims auralization client properties
    enable_auralization_client = BoolProperty(
            name="Launch EVERTims auralization client",
            description='Launch the EVERTims auralization client as a subprocess (embedded in Blender)',
            default=False,
            )

class EVERTimsPreferences(AddonPreferences):
    bl_idname = __name__

    raytracing_client_path_to_binary = StringProperty(
            name="EVERTims Raytracing client binary path",
            description="Path to the ims binary that handles EVERTims raytracing",
            default="//", maxlen=1024, subtype="FILE_PATH",
            )
    raytracing_client_path_to_matFile = StringProperty(
            name="EVERTims Raytracing client material path",
            description="Path to the .mat file used by the EVERTims raytracing client",
            default="//", maxlen=1024, subtype="FILE_PATH",
            )
    auralization_client_path_to_binary = StringProperty(
            name="EVERTims auralization client binary path",
            description="Path to the binary that handles EVERTims auralization",
            default="//", maxlen=1024, subtype="FILE_PATH",
            )

# ############################################################
# Un/Registration
# ############################################################

def register():

    bpy.utils.register_class(EVERTimsSettings)
    bpy.utils.register_class(EVERTimsPreferences)

    ui.register()
    operators.register()

    bpy.types.Scene.evertims = PointerProperty(type=EVERTimsSettings)


def unregister():

    bpy.utils.unregister_class(EVERTimsSettings)
    bpy.utils.unregister_class(EVERTimsPreferences)

    ui.unregister()
    operators.unregister()

    del bpy.types.Scene.evertims
