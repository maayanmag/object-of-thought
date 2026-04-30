"""
Species 2: The Bone-Grinder (v3 — Printable)
Uses Blender primitive objects + boolean union for guaranteed manifold meshes.
Lumps are UV spheres, scaled and displaced, then boolean-unioned with the base.

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python src/generate_bone_grinders_v3.py
"""

import bpy
import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BONE_GRINDER_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, BONE_GRINDERS_DIR
from utils import clear_scene, export_stl, mm_to_m


def create_base():
    """Create bookmark base as a cube primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mm_to_m(BASE_THICKNESS / 2)))
    obj = bpy.context.active_object
    obj.scale = (mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), mm_to_m(BASE_THICKNESS))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def boolean_union(target, tool):
    """Boolean union tool into target, remove tool object."""
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new(name="Bool", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tool
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier="Bool")
    bpy.data.objects.remove(tool, do_unlink=True)


def add_lump(x, y, base_z, width, depth, height, seed, subdivisions=3):
    """Create organic lump (sphere with displacement). Returns object."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8,
        radius=1.0,
        location=(x, y, base_z + height * 0.3)
    )
    lump = bpy.context.active_object
    lump.scale = (width / 2, depth / 2, height / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Subtle displacement for organic feel
    tex = bpy.data.textures.new(name=f"LumpTex_{seed}", type='CLOUDS')
    tex.noise_scale = 0.5
    disp = lump.modifiers.new(name="Displace", type='DISPLACE')
    disp.texture = tex
    disp.strength = mm_to_m(1.5)
    bpy.ops.object.modifier_apply(modifier="Displace")
    
    return lump


def build_bone_grinder_monolithic(seed):
    """Single dense lump, off-center weight."""
    rng = random.Random(seed)
    cfg = BONE_GRINDER_CONFIG["variants"]["monolithic"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS) * 0.5  # start inside base for boolean overlap
    
    lump = add_lump(
        x=mm_to_m(cfg["offset_x"]),
        y=mm_to_m(cfg["offset_y"]),
        base_z=base_z,
        width=mm_to_m(cfg["body_width"]),
        depth=mm_to_m(cfg["body_depth"]),
        height=mm_to_m(cfg["height"]),
        seed=seed
    )
    boolean_union(base, lump)
    
    return base


def build_bone_grinder_scattered_bumps(seed):
    """5-6 separate nodules distributed chaotically."""
    rng = random.Random(seed)
    cfg = BONE_GRINDER_CONFIG["variants"]["scattered_bumps"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS) * 0.5  # start inside base for boolean overlap
    hw = mm_to_m(BASE_WIDTH) / 2
    hh = mm_to_m(BASE_HEIGHT) / 2
    
    for i in range(cfg["count"]):
        x = rng.uniform(-hw * 0.7, hw * 0.7)
        y = rng.uniform(-hh * 0.7, hh * 0.7)
        h = mm_to_m(rng.uniform(*cfg["height_range"]))
        w = mm_to_m(cfg["body_width"]) * rng.uniform(0.7, 1.3)
        d = mm_to_m(cfg["body_depth"]) * rng.uniform(0.7, 1.3)
        
        lump = add_lump(x, y, base_z, w, d, h, seed=seed + i)
        boolean_union(base, lump)
    
    return base


def build_bone_grinder_ridge_spine(seed):
    """Continuous raised ridge along full length."""
    rng = random.Random(seed)
    cfg = BONE_GRINDER_CONFIG["variants"]["ridge_spine"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS) * 0.5  # start inside base for boolean overlap
    
    # Elongated cylinder for the ridge
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=mm_to_m(cfg["body_width"]) / 2,
        depth=mm_to_m(cfg["body_depth"]),
        location=(0, 0, base_z + mm_to_m(cfg["height"]) * 0.3)
    )
    ridge = bpy.context.active_object
    ridge.scale[2] = 1.0
    # Rotate to lie along Y axis
    ridge.rotation_euler[0] = math.radians(90)
    # Flatten vertically
    ridge.scale[0] = 1.0
    ridge.scale[1] = mm_to_m(cfg["height"]) / (mm_to_m(cfg["body_width"]) / 2)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Displacement
    tex = bpy.data.textures.new(name=f"RidgeTex_{seed}", type='CLOUDS')
    tex.noise_scale = 0.8
    disp = ridge.modifiers.new(name="Displace", type='DISPLACE')
    disp.texture = tex
    disp.strength = mm_to_m(1.0)
    bpy.ops.object.modifier_apply(modifier="Displace")
    
    boolean_union(base, ridge)
    
    return base


def build_bone_grinder_crystalline_shards(seed):
    """Jagged fragments — sharp, hostile."""
    rng = random.Random(seed)
    cfg = BONE_GRINDER_CONFIG["variants"]["crystalline_shards"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS) * 0.5  # start inside base for boolean overlap
    hw = mm_to_m(BASE_WIDTH) / 2
    hh = mm_to_m(BASE_HEIGHT) / 2
    
    for i in range(cfg["count"]):
        x = rng.uniform(-hw * 0.6, hw * 0.6)
        y = rng.uniform(-hh * 0.6, hh * 0.6)
        h = mm_to_m(rng.uniform(*cfg["height_range"]))
        w = mm_to_m(cfg["body_width"]) * rng.uniform(0.6, 1.0)
        d = mm_to_m(cfg["body_depth"]) * rng.uniform(0.6, 1.0)
        
        # Use cube (sharp edges) instead of sphere
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, y, base_z + h * 0.3)
        )
        shard = bpy.context.active_object
        shard.scale = (w, d, h)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Random rotation for jagged feel
        shard.rotation_euler[0] = math.radians(rng.uniform(-20, 20))
        shard.rotation_euler[1] = math.radians(rng.uniform(-20, 20))
        shard.rotation_euler[2] = math.radians(rng.uniform(-45, 45))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        boolean_union(base, shard)
    
    return base

def _make_textured_bookmark(seed, thickness_mm, subdiv_level, layers):
    """Smooth base + textured top. Single mesh, voxel remesh for guaranteed manifold."""

    # Start with a cube (the smooth base slab)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mm_to_m(BASE_THICKNESS / 2)))
    obj = bpy.context.active_object
    obj.scale = (mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), mm_to_m(BASE_THICKNESS))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Subdivide top face only: select top, subdivide, displace
    # Instead: subdivide entire mesh, then use vertex group
    sub = obj.modifiers.new(name="Subdiv", type='SUBSURF')
    sub.subdivision_type = 'SIMPLE'
    sub.levels = subdiv_level
    bpy.ops.object.modifier_apply(modifier="Subdiv")

    # Vertex group: only top surface gets displaced
    vg = obj.vertex_groups.new(name="Top")
    max_z = max(v.co.z for v in obj.data.vertices)
    threshold = max_z * 0.5
    for v in obj.data.vertices:
        if v.co.z >= threshold:
            weight = (v.co.z - threshold) / (max_z - threshold) if max_z > threshold else 1.0
            vg.add([v.index], weight, 'REPLACE')
        else:
            vg.add([v.index], 0.0, 'REPLACE')

    # Apply displacement layers (top only)
    for i, (tex_type, noise_scale, noise_params, strength) in enumerate(layers):
        tex = bpy.data.textures.new(name=f"Tex_{seed}_{i}", type=tex_type)
        tex.noise_scale = noise_scale
        for k, v in noise_params.items():
            setattr(tex, k, v)
        disp = obj.modifiers.new(name=f"Disp_{i}", type='DISPLACE')
        disp.texture = tex
        disp.strength = mm_to_m(strength)
        disp.direction = 'Z'
        disp.mid_level = 0.0
        disp.vertex_group = "Top"
        bpy.ops.object.modifier_apply(modifier=f"Disp_{i}")

    # Voxel remesh: guarantees manifold, no non-manifold edges ever
    vox = obj.modifiers.new(name="Voxel", type='REMESH')
    vox.mode = 'VOXEL'
    vox.voxel_size = mm_to_m(1.0)  # 1mm voxels
    bpy.ops.object.modifier_apply(modifier="Voxel")

    return obj


def build_bone_grinder_geological(seed):
    """Basalt texture — moderate bumps, no overhangs, supportless printing."""
    return _make_textured_bookmark(seed, thickness_mm=4.0, subdiv_level=5, layers=[
        ('VORONOI', 0.003, {'noise_intensity': 1.5}, 2.5),
        ('CLOUDS', 0.001, {'noise_depth': 4}, 0.8),
    ])


def build_bone_grinder_brutalist(seed):
    """Brutalist slab — chunky ridges, supportless."""
    return _make_textured_bookmark(seed, thickness_mm=4.0, subdiv_level=5, layers=[
        ('MUSGRAVE', 0.004, {'noise_intensity': 1.5}, 3.0),
        ('CLOUDS', 0.002, {'noise_depth': 3}, 0.8),
    ])


def build_bone_grinder_flint(seed):
    """Flint-like — sharp but shallow, supportless."""
    return _make_textured_bookmark(seed, thickness_mm=4.0, subdiv_level=5, layers=[
        ('VORONOI', 0.002, {'noise_intensity': 2.0}, 2.0),
        ('MUSGRAVE', 0.005, {'noise_intensity': 1.5}, 1.0),
    ])


def build_bone_grinder_corroded_surface(seed):
    """Alias — runs the geological variant."""
    return build_bone_grinder_geological(seed)



BUILDERS = {
    "monolithic": build_bone_grinder_monolithic,
    "scattered_bumps": build_bone_grinder_scattered_bumps,
    "ridge_spine": build_bone_grinder_ridge_spine,
    "crystalline_shards": build_bone_grinder_crystalline_shards,
    "corroded_surface": build_bone_grinder_corroded_surface,
    "geological": build_bone_grinder_geological,
    "brutalist": build_bone_grinder_brutalist,
    "flint": build_bone_grinder_flint,
}


def main():
    os.makedirs(BONE_GRINDERS_DIR, exist_ok=True)
    
    for variant_name, cfg in BONE_GRINDER_CONFIG["variants"].items():
        seed = cfg["seed"]
        print(f"\n[BoneGrinder: {variant_name}] Seed={seed}")
        
        clear_scene()
        builder = BUILDERS[variant_name]
        obj = builder(seed)
        
        
        out_path = os.path.join(BONE_GRINDERS_DIR, f"BoneGrinder_{variant_name}.stl")
        export_stl(obj, out_path)
        print(f"  → Exported: {out_path}")
    
    print("\n✓ Bone-Grinder generation complete")


if __name__ == "__main__":
    main()
