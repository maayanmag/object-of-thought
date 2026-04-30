"""
Species 1: The Piercer (Redesigned)
Spikes grow FROM the flat bookmark base edges and surface.
The base (40×130×2mm) remains recognizable and insertable.
Spikes are asymmetric, thorny, and make the book impossible to hold or stack.

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_piercers_v2.py
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
    PIERCER_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, PIERCERS_DIR
)
from utils import clear_scene, export_stl, mm_to_m
from bookmark_base import create_base_tongue


def build_piercer_mesh(seed, spike_count, cfg):
    """
    Build Piercer: flat bookmark base + spikes projecting from top and edges.
    Spikes are short (12-25mm) and maintain the base as the primary visible form.
    """
    rng = random.Random(seed)

    mesh = bpy.data.meshes.new(f"piercer_mesh_{seed}")
    bm = bmesh.new()

    # --- Base tongue (flat, recognizable) ---
    w = mm_to_m(BASE_WIDTH)
    h = mm_to_m(BASE_HEIGHT)
    t = mm_to_m(BASE_THICKNESS)
    hw, hh, ht = w / 2, h / 2, t / 2

    # Create base quad
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

    # --- Spikes ---
    # Place spikes on top surface and along edges, asymmetrically
    spike_length_range = cfg["spike_length_range"]
    spike_base_radius_range = cfg["spike_base_radius_range"]
    spike_tilt_range = cfg["spike_tilt_range"]

    spike_placements = []

    # Top surface: distribute spike_count spikes randomly
    for i in range(spike_count):
        sx = rng.uniform(-hw * 0.8, hw * 0.8)  # avoid very edges
        sy = rng.uniform(-hh * 0.7, hh * 0.7)  # favor center-ish
        spike_placements.append((sx, sy, mm_to_m(BASE_THICKNESS)))

    # Build spikes as tapered cones
    for placement_idx, (px, py, pz) in enumerate(spike_placements):
        spike_height = mm_to_m(rng.uniform(*spike_length_range))
        spike_base_r = mm_to_m(rng.uniform(*spike_base_radius_range))
        spike_tip_r = mm_to_m(cfg["spike_tip_radius"])

        tilt_angle = math.radians(rng.uniform(*spike_tilt_range))
        tilt_dir = rng.uniform(0, 2 * math.pi)

        # Tip position after tilt
        tip_x = px + spike_height * math.sin(tilt_angle) * math.cos(tilt_dir)
        tip_y = py + spike_height * math.sin(tilt_angle) * math.sin(tilt_dir)
        tip_z = pz + spike_height * math.cos(tilt_angle)

        # Create cone: base circle at (px, py, pz) with radius spike_base_r
        # tip at (tip_x, tip_y, tip_z) with radius spike_tip_r
        num_sides = 6  # hexagon for 3D printing
        base_verts_cone = []
        tip_verts_cone = []

        for side in range(num_sides):
            angle = 2 * math.pi * side / num_sides
            bx = px + spike_base_r * math.cos(angle)
            by = py + spike_base_r * math.sin(angle)
            bv = bm.verts.new((bx, by, pz))
            base_verts_cone.append(bv)

            tx = tip_x + spike_tip_r * math.cos(angle)
            ty = tip_y + spike_tip_r * math.sin(angle)
            tv = bm.verts.new((tx, ty, tip_z))
            tip_verts_cone.append(tv)

        # Create cone faces
        for side in range(num_sides):
            next_side = (side + 1) % num_sides
            # Side face
            bm.faces.new([base_verts_cone[side], base_verts_cone[next_side],
                         tip_verts_cone[next_side], tip_verts_cone[side]])

        # Base face (closed ring on base)
        bm.faces.new(base_verts_cone)

    # Convert to object
    obj = bpy.data.objects.new("piercer", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Voxel remesh for fusion + organic texture
    voxel_mod = obj.modifiers.new(name="Voxel", type='REMESH')
    voxel_mod.mode = 'VOXEL'
    voxel_mod.voxel_size = 0.0008  # 0.8mm voxel
    bpy.ops.object.modifier_apply(modifier=voxel_mod.name)

    # Add Voronoi texture for thorn-like surface
    tex = bpy.data.textures.new(name=f"ThornVoronoi_{seed}", type='VORONOI')
    tex.noise_scale = 3.0 / 1000.0

    disp_mod = obj.modifiers.new(name="Displace", type='DISPLACE')
    disp_mod.texture = tex
    disp_mod.strength = cfg["displacement_strength"] / 1000.0
    disp_mod.mid_level = 0.5

    bpy.ops.object.modifier_apply(modifier=disp_mod.name)

    return obj


def generate_piercers():
    """Generate 4 Piercer variations and export as STLs."""
    clear_scene()

    spike_counts = PIERCER_CONFIG["spike_counts"]
    seeds = PIERCER_CONFIG["seeds"]

    for i, (count, seed) in enumerate(zip(spike_counts, seeds)):
        print(f"\n[Piercer {i+1}] Spikes={count}, Seed={seed}")

        obj = build_piercer_mesh(seed, count, PIERCER_CONFIG)
        obj.name = f"Piercer_{i+1}_s{count}"

        # Recenter
        bbox_center = sum((Vector(b) for b in [v.co for v in obj.data.vertices]), Vector()) / len(obj.data.vertices)
        for v in obj.data.vertices:
            v.co -= bbox_center
        obj.location = (0, 0, 0)

        # Export
        filename = f"Piercer_{i+1}_s{count}.stl"
        filepath = os.path.join(PIERCERS_DIR, filename)
        export_stl(obj, filepath)
        print(f"  → Exported: {filename}")

        bpy.data.objects.remove(obj, do_unlink=True)


if __name__ == "__main__":
    os.makedirs(PIERCERS_DIR, exist_ok=True)
    generate_piercers()
    print("\n✓ Piercer generation complete")
