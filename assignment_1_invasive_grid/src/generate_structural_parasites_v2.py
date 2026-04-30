"""
Species 3: The Structural Parasite (Redesigned)
Minimal vertical fins that force pages apart. Not a cage, but a prop.
The base remains a flat bookmark. The fins are thin and sparse, so the 
pages can't close — the book becomes an involuntary sculpture.

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_structural_parasites_v2.py
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
    STRUCTURAL_PARASITE_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, STRUCTURAL_PARASITES_DIR
)
from utils import clear_scene, export_stl, mm_to_m
from bookmark_base import create_base_tongue


def build_structural_parasite_mesh(seed, opening_angle, cfg):
    """
    Build Structural Parasite: flat base tongue + minimal vertical fins.
    The fins are thin ribs that force the book open at `opening_angle` degrees.
    """
    rng = random.Random(seed)

    mesh = bpy.data.meshes.new(f"structural_parasite_mesh_{seed}")
    bm = bmesh.new()

    # --- Base tongue ---
    w = mm_to_m(BASE_WIDTH)
    h = mm_to_m(BASE_HEIGHT)
    t = mm_to_m(BASE_THICKNESS)
    hw, hh, ht = w / 2, h / 2, t / 2

    # Create base as quad
    base_verts = [
        bm.verts.new((-hw, -hh, 0)),
        bm.verts.new((hw, -hh, 0)),
        bm.verts.new((hw, hh, 0)),
        bm.verts.new((-hw, hh, 0)),
    ]
    base_face = bm.faces.new(base_verts)

    # Solidify base
    bm.faces.ensure_lookup_table()
    geom = bmesh.ops.extrude_face_region(bm, geom=[base_face])
    verts_top = [v for v in geom['geom'] if isinstance(v, bmesh.types.BMVert)]
    for v in verts_top:
        v.co.z += mm_to_m(BASE_THICKNESS)

    # --- Vertical fins ---
    # 2 thin parallel ribs growing from the base at an angle to force pages apart
    fin_height = mm_to_m(cfg["fin_height"])
    fin_thickness = mm_to_m(cfg["fin_thickness"])
    fin_width = mm_to_m(cfg["fin_width"])

    angle_rad = math.radians(opening_angle)

    # Rib 1: offset left
    rib1_x = mm_to_m(-8.0)
    for offset, rib_num in [(mm_to_m(-6), 1), (mm_to_m(6), 2)]:
        # Rib as a thin vertical wedge angled at opening_angle
        rib_verts = []

        # Bottom corners (on base)
        bottom_left = bm.verts.new((rib1_x - fin_width / 2, offset - fin_thickness / 2, mm_to_m(BASE_THICKNESS)))
        bottom_right = bm.verts.new((rib1_x + fin_width / 2, offset - fin_thickness / 2, mm_to_m(BASE_THICKNESS)))
        bottom_back_left = bm.verts.new((rib1_x - fin_width / 2, offset + fin_thickness / 2, mm_to_m(BASE_THICKNESS)))
        bottom_back_right = bm.verts.new((rib1_x + fin_width / 2, offset + fin_thickness / 2, mm_to_m(BASE_THICKNESS)))

        # Top corners (angled)
        top_x = fin_height * math.sin(angle_rad)
        top_z = fin_height * math.cos(angle_rad)

        top_left = bm.verts.new((rib1_x - fin_width / 2 + top_x, offset - fin_thickness / 2, mm_to_m(BASE_THICKNESS) + top_z))
        top_right = bm.verts.new((rib1_x + fin_width / 2 + top_x, offset - fin_thickness / 2, mm_to_m(BASE_THICKNESS) + top_z))
        top_back_left = bm.verts.new((rib1_x - fin_width / 2 + top_x, offset + fin_thickness / 2, mm_to_m(BASE_THICKNESS) + top_z))
        top_back_right = bm.verts.new((rib1_x + fin_width / 2 + top_x, offset + fin_thickness / 2, mm_to_m(BASE_THICKNESS) + top_z))

        rib_verts = [bottom_left, bottom_right, bottom_back_right, bottom_back_left,
                     top_left, top_right, top_back_right, top_back_left]

        # Create faces (front, back, left, right, top, bottom)
        bm.faces.new([bottom_left, bottom_right, top_right, top_left])  # front
        bm.faces.new([bottom_back_left, bottom_back_right, top_back_right, top_back_left])  # back
        bm.faces.new([bottom_left, bottom_back_left, top_back_left, top_left])  # left
        bm.faces.new([bottom_right, bottom_back_right, top_back_right, top_right])  # right
        bm.faces.new([top_left, top_right, top_back_right, top_back_left])  # top

    # Convert to object
    obj = bpy.data.objects.new("structural_parasite", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Optional: subtle displacement for organic quality
    if cfg.get("displacement_strength", 0) > 0:
        tex = bpy.data.textures.new(name=f"ParasiteNoise_{seed}", type='CLOUDS')
        tex.noise_scale = 8.0 / 1000.0

        disp_mod = obj.modifiers.new(name="Displace", type='DISPLACE')
        disp_mod.texture = tex
        disp_mod.strength = cfg["displacement_strength"] / 1000.0
        disp_mod.mid_level = 0.5

        bpy.ops.object.modifier_apply(modifier=disp_mod.name)

    return obj


def generate_structural_parasites():
    """Generate 3 Structural Parasite variations and export as STLs."""
    clear_scene()

    angles = STRUCTURAL_PARASITE_CONFIG["opening_angles"]
    seeds = STRUCTURAL_PARASITE_CONFIG["seeds"]

    for i, (angle, seed) in enumerate(zip(angles, seeds)):
        print(f"\n[Structural Parasite {i+1}] Angle={angle}°, Seed={seed}")

        obj = build_structural_parasite_mesh(seed, angle, STRUCTURAL_PARASITE_CONFIG)
        obj.name = f"StructuralParasite_{i+1}_a{int(angle)}"

        # Recenter
        bbox_center = sum((Vector(b) for b in [v.co for v in obj.data.vertices]), Vector()) / len(obj.data.vertices)
        for v in obj.data.vertices:
            v.co -= bbox_center
        obj.location = (0, 0, 0)

        # Export
        filename = f"StructuralParasite_{i+1}_a{int(angle)}.stl"
        filepath = os.path.join(STRUCTURAL_PARASITES_DIR, filename)
        export_stl(obj, filepath)
        print(f"  → Exported: {filename}")

        bpy.data.objects.remove(obj, do_unlink=True)


if __name__ == "__main__":
    os.makedirs(STRUCTURAL_PARASITES_DIR, exist_ok=True)
    generate_structural_parasites()
    print("\n✓ Structural Parasite generation complete")
