"""
Species 1: The Piercer
Jagged, non-Euclidean spikes extending beyond book margins.
Makes the book impossible to hold, shelve, or stack.

All geometry built in bmesh + voxel remesh to produce a single
fused, watertight, organic-looking solid.

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_piercers.py
"""

import bpy
import bmesh
import sys
import os
import math
import random
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    PIERCER_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, PIERCERS_DIR
)
from utils import clear_scene, export_stl, mm_to_m
from bookmark_base import create_base_tongue


def build_piercer_mesh(seed, spike_count, cfg):
    """
    Build Piercer: flat bookmark base (40×130×2mm) with spikes projecting from
    the top surface and edges. The base remains flat and insertable between pages.
    Spikes create the 'weaponized' appearance.
    """
    rng = random.Random(seed)

    mesh = bpy.data.meshes.new(f"piercer_mesh_{seed}")
    bm = bmesh.new()

    # --- Base tongue (flat, recognizable as a bookmark) ---
    w = mm_to_m(BASE_WIDTH)
    h = mm_to_m(BASE_HEIGHT)
    t = mm_to_m(BASE_THICKNESS)
    hw, hh, ht = w / 2, h / 2, t / 2

    def add_box(cx, cy, cz, sx, sy, sz):
        verts = [
            bm.verts.new((cx - sx, cy - sy, cz - sz)),
            bm.verts.new((cx + sx, cy - sy, cz - sz)),
            bm.verts.new((cx + sx, cy + sy, cz - sz)),
            bm.verts.new((cx - sx, cy + sy, cz - sz)),
            bm.verts.new((cx - sx, cy - sy, cz + sz)),
            bm.verts.new((cx + sx, cy - sy, cz + sz)),
            bm.verts.new((cx + sx, cy + sy, cz + sz)),
            bm.verts.new((cx - sx, cy + sy, cz + sz)),
        ]
        faces = [
            (0, 1, 2, 3), (4, 7, 6, 5),
            (0, 4, 5, 1), (2, 6, 7, 3),
            (0, 3, 7, 4), (1, 5, 6, 2),
        ]
        for fi in faces:
            bm.faces.new([verts[i] for i in fi])

    add_box(0, 0, base_t / 2, hw, hh, base_t / 2)

    # --- Spikes (cones built as fan geometry, penetrating into base) ---
    def add_cone(cx, cy, base_z, radius_bottom, radius_top, length, tilt_x, tilt_y, segments=10):
        """Add a cone to the bmesh. base_z is bottom of cone (can be inside the base tongue)."""
        verts_bottom = []
        verts_top = []
        tip_z = base_z + length

        # Build ring of vertices at bottom and top
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            # Bottom ring
            bx = cx + radius_bottom * math.cos(angle)
            by = cy + radius_bottom * math.sin(angle)
            bz = base_z
            # Top ring
            tx = cx + radius_top * math.cos(angle)
            ty = cy + radius_top * math.sin(angle)
            tz = tip_z

            # Apply tilt (rotate around base center)
            # Tilt X
            by_r = by - cy
            bz_r = bz - base_z
            by2 = cy + by_r * math.cos(tilt_x) - bz_r * math.sin(tilt_x)
            bz2 = base_z + by_r * math.sin(tilt_x) + bz_r * math.cos(tilt_x)

            ty_r = ty - cy
            tz_r = tz - base_z
            ty2 = cy + ty_r * math.cos(tilt_x) - tz_r * math.sin(tilt_x)
            tz2 = base_z + ty_r * math.sin(tilt_x) + tz_r * math.cos(tilt_x)

            # Tilt Y
            bx_r = bx - cx
            bz_r2 = bz2 - base_z
            bx2 = cx + bx_r * math.cos(tilt_y) + bz_r2 * math.sin(tilt_y)
            bz3 = base_z - bx_r * math.sin(tilt_y) + bz_r2 * math.cos(tilt_y)

            tx_r = tx - cx
            tz_r2 = tz2 - base_z
            tx2 = cx + tx_r * math.cos(tilt_y) + tz_r2 * math.sin(tilt_y)
            tz3 = base_z - tx_r * math.sin(tilt_y) + tz_r2 * math.cos(tilt_y)

            verts_bottom.append(bm.verts.new((bx2, by2, bz3)))
            verts_top.append(bm.verts.new((tx2, ty2, tz3)))

        # Side faces
        for i in range(segments):
            j = (i + 1) % segments
            bm.faces.new([verts_bottom[i], verts_bottom[j], verts_top[j], verts_top[i]])

        # Bottom cap
        bm.faces.new(verts_bottom[::-1])
        # Top cap
        bm.faces.new(verts_top)

    min_len, max_len = cfg["spike_length_range"]
    min_r, max_r = cfg["spike_base_radius_range"]
    tip_r = cfg["spike_tip_radius"]
    min_tilt, max_tilt = cfg["spike_tilt_range"]

    for i in range(spike_count):
        # Position on the tongue surface — bias toward edges and top
        if rng.random() > 0.3:
            # Edge placement — spikes near the borders
            side = rng.choice(['left', 'right', 'top'])
            if side == 'left':
                x = rng.uniform(-hw * 0.9, -hw * 0.3)
                y = rng.uniform(-hh * 0.5, hh * 0.8)
            elif side == 'right':
                x = rng.uniform(hw * 0.3, hw * 0.9)
                y = rng.uniform(-hh * 0.5, hh * 0.8)
            else:  # top
                x = rng.uniform(-hw * 0.7, hw * 0.7)
                y = rng.uniform(hh * 0.3, hh * 0.9)
        else:
            # Some scattered across the surface
            x = rng.uniform(-hw * 0.6, hw * 0.6)
            y = rng.uniform(-hh * 0.2, hh * 0.6)

        # Spike grows from INSIDE the base (penetration for fusion)
        base_z_start = mm_to_m(BASE_THICKNESS * 0.3)  # starts inside the tongue

        length = mm_to_m(rng.uniform(min_len, max_len))
        base_r = mm_to_m(rng.uniform(min_r, max_r))
        top_r = mm_to_m(tip_r)

        # Tilt direction: spikes lean OUTWARD from center
        dist_from_center = math.sqrt(x * x + y * y)
        outward_angle = math.atan2(y, x) if dist_from_center > 0.001 else rng.uniform(0, 2 * math.pi)

        tilt_magnitude = math.radians(rng.uniform(min_tilt, max_tilt))
        tilt_x = tilt_magnitude * math.sin(outward_angle)
        tilt_y = tilt_magnitude * math.cos(outward_angle)

        add_cone(x, y, base_z_start, base_r, top_r, length, tilt_x, tilt_y, segments=8)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(f"piercer_{seed}", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def fuse_with_remesh(obj, voxel_size_mm=0.8):
    """Voxel remesh to fuse all overlapping geometry into one watertight solid."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mod = obj.modifiers.new(name="Remesh", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = mm_to_m(voxel_size_mm)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def add_thorn_displacement(obj, seed, strength_mm=0.6):
    """Displacement for organic texture on the fused mesh."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    tex = bpy.data.textures.new(name=f"ThornNoise_{seed}", type='VORONOI')
    tex.noise_scale = 0.4
    tex.distance_metric = 'DISTANCE'

    disp = obj.modifiers.new(name="Displace", type='DISPLACE')
    disp.texture = tex
    disp.strength = mm_to_m(strength_mm)
    disp.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=disp.name)


def generate_piercer(variation_index, cfg):
    """Generate one Piercer bookmark variation."""
    clear_scene()
    seed = cfg["seeds"][variation_index]
    spike_count = cfg["spike_counts"][variation_index]

    print(f"\n=== Generating Piercer {variation_index + 1}/{cfg['count']} "
          f"(seed={seed}, spikes={spike_count}) ===")

    # Build the entire piercer as one bmesh
    piercer = build_piercer_mesh(seed, spike_count, cfg)

    # Fuse all geometry with voxel remesh
    # Smaller voxel = more detail but slower; 0.7mm is good for these sizes
    fuse_with_remesh(piercer, voxel_size_mm=0.7)

    # Add organic displacement texture
    add_thorn_displacement(piercer, seed, strength_mm=cfg["displacement_strength"])

    piercer.name = f"piercer_{variation_index + 1}"

    filepath = os.path.join(PIERCERS_DIR, f"piercer_{variation_index + 1}.stl")
    export_stl(piercer, filepath)
    return filepath


def main():
    """Generate all Piercer variations."""
    cfg = PIERCER_CONFIG
    print(f"\n{'='*60}")
    print(f"THE PIERCER — Generating {cfg['count']} variations")
    print(f"{'='*60}")

    generated = []
    for i in range(cfg["count"]):
        path = generate_piercer(i, cfg)
        generated.append(path)

    print(f"\n✓ Generated {len(generated)} Piercers")
    for p in generated:
        print(f"  {p}")
    return generated


if __name__ == "__main__":
    main()
