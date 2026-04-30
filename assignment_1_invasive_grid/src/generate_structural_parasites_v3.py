"""
Species 3: The Structural Parasite (v3 — Printable)
Uses Blender primitives + boolean union. Fin rotation origin is at the base
attachment point so tilted fins stay connected.
"""

import bpy
import sys
import os
import math
import random
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import STRUCTURAL_PARASITE_CONFIG, BASE_WIDTH, BASE_HEIGHT, BASE_THICKNESS, STRUCTURAL_PARASITES_DIR
from utils import clear_scene, export_stl, mm_to_m


def create_base():
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, mm_to_m(BASE_THICKNESS / 2)))
    obj = bpy.context.active_object
    obj.scale = (mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), mm_to_m(BASE_THICKNESS))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def boolean_union(target, tool):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new(name="Bool", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tool
    mod.solver = 'FLOAT'
    bpy.ops.object.modifier_apply(modifier="Bool")
    bpy.data.objects.remove(tool, do_unlink=True)


def add_fin_at(x, y, base_z, width, thickness, height, tilt_x=0, tilt_y=0, twist_z=0):
    """Create fin with origin at its BASE (attachment point), so tilt rotates from there."""
    # Create cube centered at origin
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    fin = bpy.context.active_object
    fin.scale = (thickness, width, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Move geometry UP so bottom face is at z=0 (origin stays at bottom)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, 0, height / 2))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Now rotate from origin (= base of fin)
    fin.rotation_euler = (tilt_x, tilt_y, twist_z)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Shift down into base for overlap
    overlap = mm_to_m(1.0)
    fin.location = (x, y, base_z - overlap)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    
    return fin


def build_structural_opposing_fins(seed):
    """Two parallel vertical fins, symmetric, leaning outward."""
    rng = random.Random(seed)
    cfg = STRUCTURAL_PARASITE_CONFIG["variants"]["opposing_fins"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    fin_h = mm_to_m(cfg["fin_height"])
    fin_t = mm_to_m(cfg["fin_thickness"])
    fin_w = mm_to_m(cfg["fin_width"])
    angle = math.radians(cfg["opening_angle"])
    
    offset = mm_to_m(8.0)
    
    fin_l = add_fin_at(-offset, 0, base_z, fin_w, fin_t, fin_h, tilt_y=-angle)
    boolean_union(base, fin_l)
    
    fin_r = add_fin_at(offset, 0, base_z, fin_w, fin_t, fin_h, tilt_y=angle)
    boolean_union(base, fin_r)
    
    return base


def build_structural_spiral_twist(seed):
    """Single fin built from stacked slabs that rotate as they ascend."""
    rng = random.Random(seed)
    cfg = STRUCTURAL_PARASITE_CONFIG["variants"]["spiral_twist"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    total_h = mm_to_m(cfg["fin_height"])
    fin_t = mm_to_m(cfg["fin_thickness"])
    fin_w = mm_to_m(cfg["fin_width"])
    twist_total = math.radians(cfg["twist_rotation"])
    tilt = math.radians(cfg["opening_angle"])
    
    segments = 6
    seg_h = total_h / segments
    overlap = mm_to_m(1.0)
    
    for i in range(segments):
        t_param = (i + 0.5) / segments
        z = base_z + i * seg_h
        twist_angle = t_param * twist_total
        lean = tilt * t_param * 0.3
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        seg = bpy.context.active_object
        seg.scale = (fin_t, fin_w, seg_h * 1.2)  # slight overlap between segments
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        seg.rotation_euler = (0, lean, twist_angle)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        # Place with overlap into base/prev segment
        seg.location = (0, 0, z - overlap * 0.5)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        
        boolean_union(base, seg)
    
    return base


def build_structural_splayed_ribcage(seed):
    """4 ribs splaying outward at different angles."""
    rng = random.Random(seed)
    cfg = STRUCTURAL_PARASITE_CONFIG["variants"]["splayed_ribcage"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    fin_h = mm_to_m(cfg["fin_height"])
    fin_t = mm_to_m(cfg["fin_thickness"])
    fin_w = mm_to_m(cfg["fin_width"])
    
    for rib_idx in range(cfg["fin_count"]):
        angle = math.radians(rng.uniform(*cfg["opening_angle_range"]))
        y_offset = mm_to_m(-30.0 + rib_idx * 20.0)
        x_sign = 1 if rib_idx % 2 == 0 else -1
        
        fin = add_fin_at(0, y_offset, base_z, fin_w, fin_t, fin_h,
                        tilt_y=angle * x_sign)
        boolean_union(base, fin)
    
    return base


def build_structural_wedge_ramp(seed):
    """Single long shallow wedge — minimalist, relentless."""
    rng = random.Random(seed)
    cfg = STRUCTURAL_PARASITE_CONFIG["variants"]["wedge_ramp"]
    
    base = create_base()
    base_z = mm_to_m(BASE_THICKNESS)
    fin_h = mm_to_m(cfg["fin_height"])
    fin_t = mm_to_m(cfg["fin_thickness"])
    fin_w = mm_to_m(cfg["fin_width"])
    angle = math.radians(cfg["opening_angle"])
    
    fin = add_fin_at(0, 0, base_z, fin_w, fin_t, fin_h, tilt_y=angle)
    boolean_union(base, fin)
    
    return base


BUILDERS = {
    "opposing_fins": build_structural_opposing_fins,
    "spiral_twist": build_structural_spiral_twist,
    "splayed_ribcage": build_structural_splayed_ribcage,
    "wedge_ramp": build_structural_wedge_ramp,
}


def main():
    os.makedirs(STRUCTURAL_PARASITES_DIR, exist_ok=True)
    
    for variant_name, cfg in STRUCTURAL_PARASITE_CONFIG["variants"].items():
        seed = cfg["seed"]
        print(f"\n[StructuralParasite: {variant_name}] Seed={seed}")
        
        clear_scene()
        builder = BUILDERS[variant_name]
        obj = builder(seed)
        
        out_path = os.path.join(STRUCTURAL_PARASITES_DIR, f"StructuralParasite_{variant_name}.stl")
        export_stl(obj, out_path)
        print(f"  → Exported: {out_path}")
    
    print("\n✓ Structural Parasite generation complete")


if __name__ == "__main__":
    main()
