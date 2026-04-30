"""
Species 2: The Bone-Grinder
Heavy, calcified mass with visceral texture.
Creates weight disparity — the bookmark becomes geological.

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_bone_grinders.py
"""

import bpy
import bmesh
import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    BONE_GRINDER_CONFIG, BASE_WIDTH, BASE_HEIGHT_SHORT,
    BASE_THICKNESS, BONE_GRINDERS_DIR
)
from utils import (
    clear_scene, export_stl, apply_all_modifiers,
    create_cube, create_sphere, boolean_difference,
    mm_to_m, set_origin_to_geometry
)
from bookmark_base import create_base_tongue


def create_mass_body(width, depth, height, offset_x=5.0, name="mass_body"):
    """
    Create the thick asymmetric slab that sits on top of the base tongue.
    Offset from center for unbalanced weight distribution.
    """
    obj = create_cube(
        name=name,
        size_x=width,
        size_y=depth,
        size_z=height,
        location=(offset_x, 0, BASE_THICKNESS + height / 2.0)
    )
    return obj


def add_calcified_displacement(obj, seed, cfg):
    """
    Multi-layer displacement for bone/coral texture:
    Layer 1: Voronoi (macro ridges)
    Layer 2: Musgrave-like noise (fine calcified grain)
    """
    bpy.context.view_layer.objects.active = obj

    # Subdivide for displacement detail
    sub_mod = obj.modifiers.new(name="Subdiv", type='SUBSURF')
    sub_mod.levels = 3
    sub_mod.render_levels = 3
    bpy.ops.object.modifier_apply(modifier=sub_mod.name)

    # Layer 1: Voronoi — bone ridge macro topology
    tex1 = bpy.data.textures.new(name=f"BoneVoronoi_{seed}", type='VORONOI')
    tex1.noise_scale = cfg["voronoi_scale"] / 1000.0
    tex1.distance_metric = 'DISTANCE_SQUARED'
    tex1.color_mode = 'INTENSITY'

    disp1 = obj.modifiers.new(name="VoronoiDisp", type='DISPLACE')
    disp1.texture = tex1
    disp1.strength = cfg["displacement_strength"] / 1000.0
    disp1.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=disp1.name)

    # Layer 2: Clouds noise — fine calcified detail
    tex2 = bpy.data.textures.new(name=f"BoneMusgrave_{seed}", type='CLOUDS')
    tex2.noise_scale = cfg["musgrave_scale"] / 1000.0
    tex2.noise_depth = 4

    disp2 = obj.modifiers.new(name="MusgraveDisp", type='DISPLACE')
    disp2.texture = tex2
    disp2.strength = (cfg["displacement_strength"] * 0.4) / 1000.0
    disp2.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=disp2.name)


def erode_edges(obj, seed, cfg):
    """
    Boolean subtract random spheres from edges for decay/erosion effect.
    """
    rng = random.Random(seed)

    # Get approximate bounding box for sphere placement
    bbox = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not bbox:
        return

    xs = [v.x for v in bbox]
    ys = [v.y for v in bbox]
    zs = [v.z for v in bbox]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    for i in range(cfg["erosion_sphere_count"]):
        r_min, r_max = cfg["erosion_sphere_radius_range"]
        radius = rng.uniform(r_min, r_max)

        # Place spheres near edges
        edge_axis = rng.choice(['x', 'y', 'z'])
        if edge_axis == 'x':
            sx = rng.choice([min_x, max_x]) * 1000
            sy = rng.uniform(min_y, max_y) * 1000
            sz = rng.uniform(min_z, max_z) * 1000
        elif edge_axis == 'y':
            sx = rng.uniform(min_x, max_x) * 1000
            sy = rng.choice([min_y, max_y]) * 1000
            sz = rng.uniform(min_z, max_z) * 1000
        else:
            sx = rng.uniform(min_x, max_x) * 1000
            sy = rng.uniform(min_y, max_y) * 1000
            sz = max_z * 1000  # top erosion only

        sphere = create_sphere(
            name=f"erosion_{i}",
            radius=radius,
            location=(sx, sy, sz)
        )
        try:
            boolean_difference(obj, sphere, apply=True)
        except Exception as e:
            print(f"  Warning: Erosion sphere {i} failed: {e}")
            if sphere.name in bpy.data.objects:
                bpy.data.objects.remove(sphere, do_unlink=True)


def generate_bone_grinder(variation_index, cfg):
    """Generate one Bone-Grinder bookmark variation."""
    clear_scene()
    seed = cfg["seeds"][variation_index]
    height = cfg["heights"][variation_index]

    print(f"\n=== Generating Bone-Grinder {variation_index + 1}/{cfg['count']} "
          f"(seed={seed}, height={height}mm) ===")

    # Create vestigial base tongue (shorter for this species)
    base = create_base_tongue(
        width=BASE_WIDTH,
        height=BASE_HEIGHT_SHORT,
        thickness=BASE_THICKNESS,
        name=f"bone_grinder_{variation_index + 1}_base"
    )

    # Create the heavy mass body
    rng = random.Random(seed)
    offset_x = rng.uniform(-5.0, 8.0)  # asymmetric placement
    body = create_mass_body(
        width=cfg["body_width"],
        depth=cfg["body_depth"],
        height=height,
        offset_x=offset_x,
        name=f"bone_grinder_{variation_index + 1}_body"
    )

    # Join base and body
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()

    grinder = bpy.context.active_object
    grinder.name = f"bone_grinder_{variation_index + 1}"

    # Apply calcified displacement
    add_calcified_displacement(grinder, seed, cfg)

    # Erode edges
    erode_edges(grinder, seed, cfg)

    # Export
    filepath = os.path.join(BONE_GRINDERS_DIR, f"bone_grinder_{variation_index + 1}.stl")
    export_stl(grinder, filepath)

    return filepath


def main():
    """Generate all Bone-Grinder variations."""
    cfg = BONE_GRINDER_CONFIG
    print(f"\n{'='*60}")
    print(f"THE BONE-GRINDER — Generating {cfg['count']} variations")
    print(f"{'='*60}")

    generated = []
    for i in range(cfg["count"]):
        path = generate_bone_grinder(i, cfg)
        generated.append(path)

    print(f"\n✓ Generated {len(generated)} Bone-Grinders")
    for p in generated:
        print(f"  {p}")
    return generated


if __name__ == "__main__":
    main()
