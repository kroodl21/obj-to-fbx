# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####
# <pep8 compliant>


bl_info = {
    "name": "FileConversionHelper",
    "author": "p2or's Batch Import Wavefront customized by Gaeun Karen Lee",
    "blender": (2, 93, 1),
    "category": "Import-Export",
}


import os
import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )


class ImportMultipleObjs(bpy.types.Operator, ImportHelper):
    """Batch Import Wavefront obj"""
    bl_idname = "import_scene.multiple_objs"
    bl_label = "Import multiple OBJ's"
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".obj"

    filter_glob = StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            )

    # Selected files
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    edges_setting: BoolProperty(
            name="Lines",
            description="Import lines and faces with 2 verts as edge",
            default=True,
            )
    smooth_groups_setting: BoolProperty(
            name="Smooth Groups",
            description="Surround smooth groups by sharp edges",
            default=True,
            )
    split_objects_setting: BoolProperty(
            name="Object",
            description="Import OBJ Objects into Blender Objects",
            default=True,
            )
    split_groups_setting: BoolProperty(
            name="Group",
            description="Import OBJ Groups into Blender Objects",
            default=True,
            )
    groups_as_vgroups_setting: BoolProperty(
            name="Poly Groups",
            description="Import OBJ groups as vertex groups",
            default=False,
            )
    image_search_setting: BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images "
                        "(Warning, may be slow)",
            default=True,
            )
    split_mode_setting: EnumProperty(
            name="Split",
            items=(('ON', "Split", "Split geometry, omits unused verts"),
                   ('OFF', "Keep Vert Order", "Keep vertex order from file"),
                   ),
            )
    clamp_size_setting: FloatProperty(
            name="Clamp Size",
            description="Clamp bounds under this value (zero to disable)",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=0.0,
            )
    axis_forward_setting: EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='-Z',
            )
    axis_up_setting: EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
            )

    #setting UI that appears on the right side of the file picker
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "smooth_groups_setting")
        row.prop(self, "edges_setting")

        box = layout.box()
        row = box.row()
        row.prop(self, "split_mode_setting", expand=True)

        row = box.row()
        if self.split_mode_setting == 'ON':
            row.label(text="Split by:")
            row.prop(self, "split_objects_setting")
            row.prop(self, "split_groups_setting")
        else:
            row.prop(self, "groups_as_vgroups_setting")

        row = layout.split(factor=0.67)
        row.prop(self, "clamp_size_setting")
        layout.prop(self, "axis_forward_setting")
        layout.prop(self, "axis_up_setting")

        layout.prop(self, "image_search_setting")


    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        def remove_default():
            #remove the camera, light and cube from the scene
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['Camera'].select_set(True) 
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['Light'].select_set(True) 
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['Cube'].select_set(True) 
            bpy.ops.object.delete()

        #need to remove the default objects before the user import obj files so that the add-on does not accidentally delete objects that happen to have the same name with the default objects such as 'Light' or 'Cube.'
        remove_default()

        def set_origin():
            #without the override, it snapping command throws 'context is incorrect' error. Override code source:https://b3d.interplanety.org/en/context-override/
            override_context = bpy.context.copy()
            area = [area for area in bpy.context.screen.areas if area.type == "VIEW_3D"][0]
            override_context['window'] = bpy.context.window
            override_context['screen'] = bpy.context.screen
            override_context['area'] = area
            override_context['region'] = area.regions[-1]
            override_context['scene'] = bpy.context.scene
            override_context['space_data'] = area.spaces.active
            #snap the cursor to the origin    
            bpy.ops.view3d.snap_cursor_to_center(override_context)
            #select all
            bpy.ops.object.select_all(action='SELECT')
            #set origin:origin to geometry
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            #snap selection to curosr(keep offset)
            bpy.ops.view3d.snap_selected_to_cursor(override_context, use_offset = True)


        # get the folder
        folder = (os.path.dirname(self.filepath))

        # iterate through the selected files
        for i in self.files:

            # generate full path to file
            path_to_file = (os.path.join(folder, i.name))

            # call obj operator and assign ui values                  
            bpy.ops.import_scene.obj(
                                filepath = path_to_file,
                                axis_forward = self.axis_forward_setting,
                                axis_up = self.axis_up_setting, 
                                use_edges = self.edges_setting,
                                use_smooth_groups = self.smooth_groups_setting, 
                                use_split_objects = self.split_objects_setting,
                                use_split_groups = self.split_groups_setting,
                                use_groups_as_vgroups = self.groups_as_vgroups_setting,
                                use_image_search = self.image_search_setting,
                                split_mode = self.split_mode_setting,
                                global_clamp_size = self.clamp_size_setting)
        set_origin()

        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportMultipleObjs.bl_idname, text="Import Mutiple OBJs")


def register():
    bpy.utils.register_class(ImportMultipleObjs)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportMultipleObjs)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    #test call
    # bpy.ops.import_scene.multiple_objs('INVOKE_DEFAULT')