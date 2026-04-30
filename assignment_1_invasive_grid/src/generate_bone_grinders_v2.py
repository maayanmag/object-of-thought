"""
Species 2: The Bone-Grinder (Redesigned)
Calcified lumps that sit ON the bookmark base (40×130×2mm).
The base remains flat and insertable. The lump stays within page width (135mm)
so the bookmark feels heavy and alien but still recognizable.

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_bone_grinders_v2.py
"""

import bpy
import bmesh
import sys
import os
import math
import random
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    BONE_GRINDER_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, BONE_GRINDERS_DIR
)
from utils import clear_scene, export_stl, mm_to_m
from bookmark_base import create_base_tongue


def build_bone_grinder_mesh(seed, height, cfg):
    """
    Build Bone-Grinder: flat base tongue + compact calcified lump on top.
    The lump is asymmetric and stays within ~28mm width (page width = 135mm).
    """
    rng = random.Random(seed)

    mesh = bpy.data.meshes.new(f"bone_grinder_mesh_{seed}")
    bm = bmesh.new()

    # --- Base tongue (flat, recognizable) ---
    w = mm_to_m(BASE_WIDTH)
    h = mm_to_m(BASE_HEIGHT)
    t = mm_to_m(BASE_THICKNESS)
    hw, hh, ht = w / 2, h / 2, t / 2

    # Create base as a simple quad (will be extruded/solidified in Blender)
    base_verts = [
        bm.verts.new((-hw, -hh, 0)),
        bm.verts.new((hw, -hh, 0)),
        bm.verts.new((hw, hh, 0)),
        bm.verts.new((-hw, hh, 0)),
    ]
    base_face = bm.faces.new(base_verts)

    # Solidify the base (extrude it to thickness)
    bm.faces.ensure_lookup_table()
    geom = bmesh.ops.extrude_face_region(bm, geom=[base_face])
    verts_top = [v for v in geom['geom'] if isinstance(v, bmesh.types.BMVert)]
    for v in verts_top:
        v.co.z += mm_to_m(BASE_THICKNESS)

    # --- Calcified lump ---
    # Asymmetric blob, roughly centered on base but offset in X
    lump_width = mm_to_m(cfg["body_width"])
    lump_depth = mm_to_m(cfg["body_depth"])
    lump_height = mm_to_m(height)

    offset_x = mm_to_m(3.0)  # slight offset for asymmetry
    offset_y = mm_to_m(rng.uniform(-5, 5))  # random Y jitter
    lump_z = mm_to_m(BASE_THICKNESS) + lump_height / 2

    lump_verts = []
    # Create a rough blob using 8 corner points + random displacement
    for dx in [-lump_width / 2, lump_width / 2]:
        for dy in [-lump_depth / 2, lump_depth / 2]:
            for dz in [-lump_height / 2, lump_height / 2]:
                # Add noise to edges for organic look
                jx = rng.uniform(-lump_width * 0.15, lump_width * 0.15)
                jy = rng.uniform(-lump_depth * 0.15, lump_depth * 0.15)
                jz = rng.uniform(-lump_height * 0.1, lump_height * 0.1) if dz > 0 else 0
                v = bm.verts.new((
                    offset_x + dx + jx,
                    offset_y + dy + jy,
                    lump_z + dz + jz
                ))
                lump_verts.append(v)

    # Create lump as a simple convex hull of these points
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # Convert to object and apply voxel remesh for fusion
    obj = bpy.data.objects.new("bone_grinder", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Voxel remesh to fuse + add organic texture
    voxel_mod = obj.modifiers.new(name="Voxel", type='REMESH')
    voxel_mod.mode = 'VOXEL'
    voxel_mod.voxel_size = 0.0008  # 0.8mm voxel
    bpy.ops.object.modifier_apply(modifier=voxel_mod.name)

    # Add Voronoi displacement for calcified texture
    tex = bpy.data.textures.new(name=f"CalcifyVoronoi_{seed}", type='VORONOI')
    tex.noise_scale = cfg["voronoi_scale"] / 1000.0

    disp_mod = obj.modifiers.new(name="Displace", type='DISPLACE')
    disp_mod.texture = tex
    disp_mod.strength = cfg["displacement_strength"] / 1000.0
    disp_mod.mid_level = 0.5

    bpy.ops.object.modifier_apply(modifier=disp_mod.name)

    return obj


def generate_bone_grinders():
    """Generate 3-4 Bone-Grinder variations and export as STLs."""
    clear_scene()

    heights = BONE_GRINDER_CONFIG["heights"]
    seeds = BONE_GRINDER_CONFIG["seeds"]

    for i, (h, seed) in enumerate(zip(heights, seeds)):
        print(f"\n[Bone-Grinder {i+1}] Height={h}mm, Seed={seed}")

        obj = build_bone_grinder_mesh(seed, h, BONE_GRINDER_CONFIG)
        obj.name = f"BoneGrinder_{i+1}_h{int(h)}"

        # Recenter to origin
        bbox_center = sum((Vector(b) for b in [v.co for v in obj.data.vertices]), Vector()) / len(obj.data.vertices)
        for v in obj.data.vertices:
            v.co -= bbox_center
        obj.location = (0, 0, 0)

        # Export
        filename = f"BoneGrinder_{i+1}_h{int(h)}.stl"
        filepath = os.path.join(BONE_GRINDERS_DIR, filename)
        export_stl(obj, filepath)
        print(f"  → Exported: {filename}")

        bpy.data.objects.remove(obj, do_unlink=True)


if __name__ == "__main__":
    os.makedirs(BONE_GRINDERS_DIR, exist_ok=True)
    generate_bone_grinders()
    print("\n✓ Bone-Grinder generation complete")
