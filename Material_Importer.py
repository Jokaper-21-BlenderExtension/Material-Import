import bpy
import os

class AJO_PT_MaterialImporter(bpy.types.Panel):
    bl_label = "Material Importer"
    bl_idname = "AJO_PT_materialimporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AJO'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Filepath for Blender files
        layout.prop(scene, "ajo_directory", text="Blender Folder")

        # Material name input
        layout.prop(scene, "ajo_material_name", text="Material Name")

        # Combined button for searching and importing
        layout.operator("ajo.search_and_import_material", text="Search & Import Material")


class AJO_OT_SearchAndImportMaterial(bpy.types.Operator):
    """Search for .blend files and import specified material"""
    bl_idname = "ajo.search_and_import_material"
    bl_label = "Search & Import Material"
    
    def execute(self, context):
        # Step 1: Search for .blend files
        directory = context.scene.ajo_directory
        if not os.path.exists(directory):
            self.report({'ERROR'}, "Directory not found")
            return {'CANCELLED'}

        # Clear previous search results
        context.scene.ajo_blend_files.clear()

        # Find all .blend files in directory and subfolders
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".blend"):
                    item = context.scene.ajo_blend_files.add()
                    item.name = os.path.join(root, file)
                    print(f"Found blend file: {item.name}")  # Logging found files

        if not context.scene.ajo_blend_files:
            self.report({'ERROR'}, "No blend files found.")
            return {'CANCELLED'}

        # Step 2: Import the specified material
        material_name = context.scene.ajo_material_name
        if not material_name:
            self.report({'ERROR'}, "Please provide a material name")
            return {'CANCELLED'}

        imported_materials = set()  # Track imported materials
        material_found = False  # Track if material is found

        # Iterate through all .blend files to find the material
        for blend_file in context.scene.ajo_blend_files:
            filepath = blend_file.name

            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                continue

            print(f"Checking file: {filepath}")  # Log the file being checked

            # Try to load the material from the current blend file
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
                print(f"Available materials in {filepath}: {data_from.materials}")  # Log available materials
                
                if material_name in data_from.materials:
                    if material_name not in imported_materials:
                        data_to.materials = [material_name]  # Import the material
                        imported_materials.add(material_name)  # Mark as imported

                        # Now set use_fake_user to False for the imported material
                        material = bpy.data.materials.get(material_name)
                        if material:
                            material.use_fake_user = False  # Ensure no fake user is created
                            material_found = True  # Mark material as found
                            self.report({'INFO'}, f"Material '{material_name}' imported from {os.path.basename(filepath)}")
                            # Notify after import
                            self.report({'INFO'}, f"Successfully imported '{material_name}'.")
                            return {'FINISHED'}  # Exit after successful import

        # If material not found in any file
        if not material_found:
            self.report({'ERROR'}, f"Material '{material_name}' not found in any blend file.")
            return {'CANCELLED'}

        return {'FINISHED'}


def register():
    bpy.utils.register_class(AJO_PT_MaterialImporter)
    bpy.utils.register_class(AJO_OT_SearchAndImportMaterial)

    bpy.types.Scene.ajo_directory = bpy.props.StringProperty(
        name="Blender Folder",
        subtype='DIR_PATH',
        default=""
    )
    bpy.types.Scene.ajo_material_name = bpy.props.StringProperty(
        name="Material Name",
        default=""
    )
    bpy.types.Scene.ajo_blend_files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)


def unregister():
    bpy.utils.unregister_class(AJO_PT_MaterialImporter)
    bpy.utils.unregister_class(AJO_OT_SearchAndImportMaterial)

    del bpy.types.Scene.ajo_directory
    del bpy.types.Scene.ajo_material_name
    del bpy.types.Scene.ajo_blend_files


if __name__ == "__main__":
    register()
