"""
Blender utility functions for The Invasive Grid project.
Run inside Blender Python context (bpy available).
"""

import bpy
import bmesh
import os
import math


def clear_scene():
    """Remove all objects, meshes, and materials from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def export_stl(obj, filepath):
    """Export a single object as STL (Blender 4.0+ / 5.0 API).
    Blender internal units are meters; STL expects mm, so scale by 1000."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(
        filepath=filepath,
        export_selected_objects=True,
        ascii_format=False,
        global_scale=1000.0
    )
    print(f"  → Exported: {filepath}")


def apply_all_modifiers(obj):
    """Apply all modifiers on an object."""
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers[:]:
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError as e:
            print(f"  Warning: Could not apply modifier {mod.name}: {e}")


def boolean_union(target, cutter, apply=True):
    """Boolean union: merge cutter into target."""
    mod = target.modifiers.new(name="BoolUnion", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = cutter
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)


def boolean_difference(target, cutter, apply=True):
    """Boolean difference: subtract cutter from target."""
    mod = target.modifiers.new(name="BoolDiff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)


def add_remesh(obj, voxel_size=0.5):
    """Apply voxel remesh for clean, printable geometry."""
    mod = obj.modifiers.new(name="Remesh", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = voxel_size / 1000.0  # Blender uses meters
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def create_cube(name, size_x, size_y, size_z, location=(0, 0, 0)):
    """Create a box mesh at the given location. Dimensions in mm (converted to meters)."""
    sx = size_x / 1000.0
    sy = size_y / 1000.0
    sz = size_z / 1000.0
    lx, ly, lz = location[0] / 1000.0, location[1] / 1000.0, location[2] / 1000.0

    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, lz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    return obj


def create_cone(name, radius1, radius2, depth, location=(0, 0, 0)):
    """Create a cone. Dimensions in mm."""
    r1 = radius1 / 1000.0
    r2 = radius2 / 1000.0
    d = depth / 1000.0
    lx, ly, lz = location[0] / 1000.0, location[1] / 1000.0, location[2] / 1000.0

    bpy.ops.mesh.primitive_cone_add(
        radius1=r1,
        radius2=r2,
        depth=d,
        vertices=12,
        location=(lx, ly, lz)
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def create_sphere(name, radius, location=(0, 0, 0)):
    """Create a UV sphere. Dimensions in mm."""
    r = radius / 1000.0
    lx, ly, lz = location[0] / 1000.0, location[1] / 1000.0, location[2] / 1000.0
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=r,
        segments=16,
        ring_count=8,
        location=(lx, ly, lz)
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def mm_to_m(v):
    """Convert millimeters to meters (Blender's native unit)."""
    return v / 1000.0


def set_origin_to_geometry(obj):
    """Set the object's origin to its geometry center."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
