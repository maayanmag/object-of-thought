"""
Species 1: The Piercer (v3 — Printable, flat bottom)
Uses Blender primitives + boolean union + bottom clip for clean print bed contact.

Variants:
1. sparse_needles: Few long aggressive spikes
2. dense_cluster: Many short blunt nubs
3. spiral_ascent: Spikes in helical pattern
4. asymmetric_eruption: One massive + satellites
5. tumor_bloom: Heavy bumpy displacement — diseased surface
"""

import bpy
import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PIERCER_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, PIERCERS_DIR
from utils import clear_scene, export_stl, mm_to_m


def create_base():
    """Create bookmark base as a cube primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mm_to_m(BASE_THICKNESS / 2)))
    obj = bpy.context.active_object
    obj.scale = (mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), mm_to_m(BASE_THICKNESS))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def add_cone_spike(sx, sy, base_z, height, base_r, tip_r, tilt_angle, tilt_dir):
    """Add cone spike with origin at BASE so tilt rotates from attachment point."""
    # Create cone centered at origin
    bpy.ops.mesh.primitive_cone_add(
        vertices=12,
        radius1=base_r,
        radius2=tip_r,
        depth=height,
        location=(0, 0, 0)
    )
    spike = bpy.context.active_object

    # Move geometry up so bottom of cone is at z=0 (origin = base of spike)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, 0, height / 2))
    bpy.ops.object.mode_set(mode='OBJECT')

    # Tilt from base attachment point
    spike.rotation_euler[0] = tilt_angle * math.cos(tilt_dir)
    spike.rotation_euler[1] = tilt_angle * math.sin(tilt_dir)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # Position: embed 1mm into base for solid boolean overlap
    overlap = mm_to_m(1.0)
    spike.location = (sx, sy, base_z - overlap)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    return spike


def boolean_union(target, tool):
    """Boolean union tool into target, remove tool object."""
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new(name="Bool", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tool
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier="Bool")
    bpy.data.objects.remove(tool, do_unlink=True)


def flatten_bottom(obj):
    """Clip everything below z=0 for flat print bed contact."""
    # Create a large clipping box above z=0
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.25))
    clipbox = bpy.context.active_object
    clipbox.scale = (0.5, 0.5, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new(name="Clip", type='BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.object = clipbox
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier="Clip")
    bpy.data.objects.remove(clipbox, do_unlink=True)


# ---- VARIANT BUILDERS ----

def build_piercer_sparse_needles(seed):
    """Few (2-3) long aggressive spikes."""
    rng = random.Random(seed)
    cfg = PIERCER_CONFIG["variants"]["sparse_needles"]

    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    hw = mm_to_m(BASE_WIDTH) / 2
    hh = mm_to_m(BASE_HEIGHT) / 2

    for i in range(cfg["spike_count"]):
        sx = rng.uniform(-hw * 0.5, hw * 0.5)
        sy = rng.uniform(-hh * 0.5, hh * 0.5)
        height = mm_to_m(rng.uniform(*cfg["spike_length_range"]))
        base_r = mm_to_m(rng.uniform(*cfg["spike_base_radius_range"]))
        tip_r = mm_to_m(cfg["spike_tip_radius"])
        tilt = math.radians(rng.uniform(*cfg["spike_tilt_range"]))
        tilt_dir = rng.uniform(0, 2 * math.pi)

        spike = add_cone_spike(sx, sy, base_z, height, base_r, tip_r, tilt, tilt_dir)
        boolean_union(base, spike)

    flatten_bottom(base)
    return base


def build_piercer_dense_cluster(seed):
    """Many (8-10) short blunt nubs."""
    rng = random.Random(seed)
    cfg = PIERCER_CONFIG["variants"]["dense_cluster"]

    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    hw = mm_to_m(BASE_WIDTH) / 2
    hh = mm_to_m(BASE_HEIGHT) / 2

    for i in range(cfg["spike_count"]):
        sx = rng.uniform(-hw * 0.7, hw * 0.7)
        sy = rng.uniform(-hh * 0.7, hh * 0.7)
        height = mm_to_m(rng.uniform(*cfg["spike_length_range"]))
        base_r = mm_to_m(rng.uniform(*cfg["spike_base_radius_range"]))
        tip_r = mm_to_m(cfg["spike_tip_radius"])
        tilt = math.radians(rng.uniform(*cfg["spike_tilt_range"]))
        tilt_dir = rng.uniform(0, 2 * math.pi)

        spike = add_cone_spike(sx, sy, base_z, height, base_r, tip_r, tilt, tilt_dir)
        boolean_union(base, spike)

    flatten_bottom(base)
    return base


def build_piercer_spiral_ascent(seed):
    """5 spikes arranged in spiral pattern."""
    rng = random.Random(seed)
    cfg = PIERCER_CONFIG["variants"]["spiral_ascent"]

    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    hw = mm_to_m(BASE_WIDTH) / 2
    spiral_r = hw * 0.4

    for i in range(cfg["spike_count"]):
        angle = 2 * math.pi * i / cfg["spike_count"]
        sx = spiral_r * math.cos(angle)
        sy = spiral_r * math.sin(angle)
        height = mm_to_m(rng.uniform(*cfg["spike_length_range"]))
        base_r = mm_to_m(rng.uniform(*cfg["spike_base_radius_range"]))
        tip_r = mm_to_m(cfg["spike_tip_radius"])
        tilt = math.radians(rng.uniform(*cfg["spike_tilt_range"]))

        spike = add_cone_spike(sx, sy, base_z, height, base_r, tip_r, tilt, angle)
        boolean_union(base, spike)

    flatten_bottom(base)
    return base


def build_piercer_asymmetric_eruption(seed):
    """One massive spike + small satellites."""
    rng = random.Random(seed)
    cfg = PIERCER_CONFIG["variants"]["asymmetric_eruption"]

    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    hw = mm_to_m(BASE_WIDTH) / 2
    hh = mm_to_m(BASE_HEIGHT) / 2

    # Dominant spike
    sx = rng.uniform(-hw * 0.3, hw * 0.3)
    sy = rng.uniform(-hh * 0.3, hh * 0.3)
    height = mm_to_m(rng.uniform(*cfg["dominant_spike_length"]))
    base_r = mm_to_m(rng.uniform(*cfg["dominant_base_radius"]))
    tip_r = mm_to_m(cfg["spike_tip_radius"])
    tilt = math.radians(rng.uniform(*cfg["spike_tilt_range"]))
    tilt_dir = rng.uniform(0, 2 * math.pi)

    spike = add_cone_spike(sx, sy, base_z, height, base_r, tip_r, tilt, tilt_dir)
    boolean_union(base, spike)

    # Satellites
    for i in range(cfg["satellite_count"]):
        sx = rng.uniform(-hw * 0.6, hw * 0.6)
        sy = rng.uniform(-hh * 0.6, hh * 0.6)
        height = mm_to_m(rng.uniform(*cfg["satellite_spike_length"]))
        base_r = mm_to_m(rng.uniform(*cfg["satellite_base_radius"]))
        tilt = math.radians(rng.uniform(10, 35))
        tilt_dir = rng.uniform(0, 2 * math.pi)

        spike = add_cone_spike(sx, sy, base_z, height, base_r, tip_r, tilt, tilt_dir)
        boolean_union(base, spike)

    flatten_bottom(base)
    return base


def build_piercer_tumor_bloom(seed):
    """Bookmark with aggressive bumpy/tumorous surface — diseased, hostile texture.
    Only the top surface gets displaced; bottom stays flat for printing."""
    rng = random.Random(seed)
    cfg = PIERCER_CONFIG["variants"]["tumor_bloom"]

    base = create_base()
    bpy.context.view_layer.objects.active = base

    # Subdivide for displacement detail
    sub = base.modifiers.new(name="Subdiv", type='SUBSURF')
    sub.levels = 4
    sub.render_levels = 4
    bpy.ops.object.modifier_apply(modifier="Subdiv")

    # Create vertex group: top half gets displaced, bottom stays
    vg = base.vertex_groups.new(name="TopSurface")
    max_z = max(v.co.z for v in base.data.vertices)
    mid_z = max_z * 0.3  # lower threshold to catch most of the top surface
    for v in base.data.vertices:
        if v.co.z >= mid_z:
            # Gradient weight: 0 at mid_z, 1 at max_z
            weight = (v.co.z - mid_z) / (max_z - mid_z) if max_z > mid_z else 1.0
            vg.add([v.index], weight, 'REPLACE')
        else:
            vg.add([v.index], 0.0, 'REPLACE')

    # Layer 1: Large tumor lumps
    tex1 = bpy.data.textures.new(name=f"TumorLarge_{seed}", type='VORONOI')
    tex1.noise_scale = 1.5
    tex1.noise_intensity = 1.5
    disp1 = base.modifiers.new(name="TumorLarge", type='DISPLACE')
    disp1.texture = tex1
    disp1.strength = mm_to_m(cfg["large_bump_strength"])
    disp1.direction = 'NORMAL'
    disp1.vertex_group = "TopSurface"
    disp1.mid_level = 0.0
    bpy.ops.object.modifier_apply(modifier="TumorLarge")

    # Layer 2: Small pox/bumps
    tex2 = bpy.data.textures.new(name=f"TumorSmall_{seed}", type='CLOUDS')
    tex2.noise_scale = 4.0
    tex2.noise_depth = 4
    disp2 = base.modifiers.new(name="TumorSmall", type='DISPLACE')
    disp2.texture = tex2
    disp2.strength = mm_to_m(cfg["small_bump_strength"])
    disp2.direction = 'NORMAL'
    disp2.vertex_group = "TopSurface"
    disp2.mid_level = 0.0
    bpy.ops.object.modifier_apply(modifier="TumorSmall")

    return base


# --- Variant dispatcher ---
BUILDERS = {
    "sparse_needles": build_piercer_sparse_needles,
    "dense_cluster": build_piercer_dense_cluster,
    "spiral_ascent": build_piercer_spiral_ascent,
    "asymmetric_eruption": build_piercer_asymmetric_eruption,
    "tumor_bloom": build_piercer_tumor_bloom,
}


def main():
    os.makedirs(PIERCERS_DIR, exist_ok=True)

    for variant_name, cfg in PIERCER_CONFIG["variants"].items():
        seed = cfg["seed"]
        print(f"\n[Piercer: {variant_name}] Seed={seed}")

        clear_scene()
        builder = BUILDERS[variant_name]
        obj = builder(seed)

        out_path = os.path.join(PIERCERS_DIR, f"Piercer_{variant_name}.stl")
        export_stl(obj, out_path)
        print(f"  → Exported: {out_path}")

    print("\n✓ Piercer generation complete")


if __name__ == "__main__":
    main()
