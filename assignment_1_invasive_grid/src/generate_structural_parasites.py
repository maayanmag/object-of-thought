"""
Species 3: The Structural Parasite
Lattice skeleton that forces the book open at unnatural angles.
Turns a flat object into an involuntary 3D sculpture.

Each of the 5 variations is a DISTINCT architectural form:
  1. Minimal Cage      — tight, low, claustrophobic grid
  2. Asymmetric Shelf  — lopsided, one side erupts
  3. Cathedral Arch    — tall central spine with flying buttresses
  4. Splayed Ribcage   — multiple wing pairs fanning outward
  5. Full Eruption     — maximum spread, dense lattice, chaotic

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_structural_parasites.py
"""

import bpy
import bmesh
import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    STRUCTURAL_PARASITE_CONFIG, BASE_WIDTH, BASE_HEIGHT,
    BASE_THICKNESS, STRUCTURAL_PARASITES_DIR
)
from utils import clear_scene, export_stl, mm_to_m
from bookmark_base import create_base_tongue


def add_box(bm, cx, cy, cz, sx, sy, sz):
    """Add a box to bmesh at center (cx,cy,cz) with half-sizes (sx,sy,sz)."""
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


def add_wedge_ramp(bm, cx, cy, width, depth, peak_height, z_base, flip=False):
    """
    Add a solid wedge/ramp that grows from z_base up to z_base + peak_height.
    Fully self-supporting on FDM: each layer sits on the previous one.
    The inclined top surface pushes pages apart.

    flip=False: ramp rises toward +Y (front)
    flip=True:  ramp rises toward -Y (back)
    """
    hw = width / 2.0
    hd = depth / 2.0
    z_lo = z_base
    z_hi = z_base + peak_height

    if flip:
        # Ramp rises toward -Y
        verts = [
            bm.verts.new((cx - hw, cy - hd, z_lo)),   # 0: back-left bottom
            bm.verts.new((cx + hw, cy - hd, z_lo)),   # 1: back-right bottom
            bm.verts.new((cx + hw, cy + hd, z_lo)),   # 2: front-right bottom
            bm.verts.new((cx - hw, cy + hd, z_lo)),   # 3: front-left bottom
            bm.verts.new((cx - hw, cy - hd, z_hi)),   # 4: back-left top (peak)
            bm.verts.new((cx + hw, cy - hd, z_hi)),   # 5: back-right top (peak)
            # front stays at z_lo — the ramp slopes down toward +Y
        ]
        # Bottom quad
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
        # Back wall (vertical)
        bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
        # Left triangle
        bm.faces.new([verts[0], verts[3], verts[4]])
        # Right triangle
        bm.faces.new([verts[1], verts[5], verts[2]])
        # Top ramp (inclined surface)
        bm.faces.new([verts[4], verts[3], verts[2], verts[5]])
    else:
        # Ramp rises toward +Y
        verts = [
            bm.verts.new((cx - hw, cy - hd, z_lo)),   # 0: back-left bottom
            bm.verts.new((cx + hw, cy - hd, z_lo)),   # 1: back-right bottom
            bm.verts.new((cx + hw, cy + hd, z_lo)),   # 2: front-right bottom
            bm.verts.new((cx - hw, cy + hd, z_lo)),   # 3: front-left bottom
            bm.verts.new((cx - hw, cy + hd, z_hi)),   # 4: front-left top (peak)
            bm.verts.new((cx + hw, cy + hd, z_hi)),   # 5: front-right top (peak)
        ]
        # Bottom quad
        bm.faces.new([verts[3], verts[2], verts[1], verts[0]])
        # Front wall (vertical)
        bm.faces.new([verts[3], verts[4], verts[5], verts[2]])
        # Left triangle
        bm.faces.new([verts[0], verts[4], verts[3]])
        # Right triangle
        bm.faces.new([verts[2], verts[5], verts[1]])
        # Top ramp (inclined surface)
        bm.faces.new([verts[0], verts[1], verts[5], verts[4]])


def build_base_tongue_bm(bm, width, height, thickness):
    """Add the base tongue to an existing bmesh."""
    hw = width / 2.0
    hh = height / 2.0
    ht = thickness / 2.0
    add_box(bm, 0, 0, ht, hw, hh, ht)


def build_lattice_grid(bm, width, depth, height, cell_size, strut_t, z_base, seed=0,
                       remove_ratio=0.0):
    """Build a lattice grid in the bmesh. remove_ratio randomly deletes struts for organic decay."""
    rng = random.Random(seed)
    sw = strut_t / 2.0
    hw = width / 2.0
    hd = depth / 2.0
    z_center = z_base + height / 2.0

    # X-direction struts
    num_y = int(depth / cell_size) + 1
    for i in range(num_y):
        y = -hd + i * cell_size
        if abs(y) > hd + 0.0001:
            continue
        if rng.random() < remove_ratio:
            continue
        add_box(bm, 0, y, z_center, hw, sw, sw)

    # Y-direction struts
    num_x = int(width / cell_size) + 1
    for i in range(num_x):
        x = -hw + i * cell_size
        if abs(x) > hw + 0.0001:
            continue
        if rng.random() < remove_ratio:
            continue
        add_box(bm, x, 0, z_center, sw, hd, sw)

    # Vertical struts
    for ix in range(0, num_x, 2):
        for iy in range(0, num_y, 2):
            x = -hw + ix * cell_size
            y = -hd + iy * cell_size
            if abs(x) > hw + 0.0001 or abs(y) > hd + 0.0001:
                continue
            if rng.random() < remove_ratio * 0.5:
                continue
            add_box(bm, x, y, z_center, sw, sw, height / 2.0)


# ============================================================
# 5 DISTINCT ARCHITECTURAL FORMS
# ============================================================

def build_v1_minimal_cage(seed):
    """Variation 1: Tight, low cage. Dense grid with gentle wedges. Fully self-supporting."""
    bm = bmesh.new()
    t = mm_to_m(BASE_THICKNESS)
    sw = mm_to_m(1.5)

    build_base_tongue_bm(bm, mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), t)

    # Small, dense grid sitting right on the tongue
    build_lattice_grid(
        bm,
        width=mm_to_m(50), depth=mm_to_m(40), height=mm_to_m(8),
        cell_size=mm_to_m(6), strut_t=sw, z_base=t,
        seed=seed, remove_ratio=0.0
    )

    # Two gentle wedge ramps on top — opposing directions push pages apart
    add_wedge_ramp(bm, 0, mm_to_m(5), mm_to_m(50), mm_to_m(25), mm_to_m(6), t + mm_to_m(8), flip=False)
    add_wedge_ramp(bm, 0, mm_to_m(-5), mm_to_m(50), mm_to_m(25), mm_to_m(6), t + mm_to_m(8), flip=True)

    return bm


def build_v2_asymmetric_shelf(seed):
    """Variation 2: Lopsided — tall wedge on one side, low on the other. Self-supporting."""
    rng = random.Random(seed)
    bm = bmesh.new()
    t = mm_to_m(BASE_THICKNESS)
    sw = mm_to_m(2.0)

    build_base_tongue_bm(bm, mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), t)

    # Asymmetric lattice — wider on the right
    build_lattice_grid(
        bm,
        width=mm_to_m(100), depth=mm_to_m(50), height=mm_to_m(12),
        cell_size=mm_to_m(12), strut_t=sw, z_base=t,
        seed=seed, remove_ratio=0.15
    )

    # Tall wedge ramp on the right (erupts past page edge)
    add_wedge_ramp(bm, mm_to_m(25), 0, mm_to_m(60), mm_to_m(45), mm_to_m(20), t, flip=False)

    # Short wedge on the left (barely there)
    add_wedge_ramp(bm, mm_to_m(-15), 0, mm_to_m(30), mm_to_m(25), mm_to_m(5), t, flip=True)

    # Vertical fin on the right edge — just a tall box, fully printable
    add_box(bm, mm_to_m(55), 0, t + mm_to_m(10), mm_to_m(1.5), mm_to_m(30), mm_to_m(10))

    return bm


def build_v3_cathedral_arch(seed):
    """Variation 3: Tall central spine with buttress wedges radiating from it. Self-supporting."""
    bm = bmesh.new()
    t = mm_to_m(BASE_THICKNESS)
    sw = mm_to_m(2.0)

    build_base_tongue_bm(bm, mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), t)

    # Tall central column (vertical = self-supporting)
    spine_h = mm_to_m(28)
    add_box(bm, 0, 0, t + spine_h / 2, mm_to_m(4), mm_to_m(60), spine_h / 2)

    # Buttress wedges growing outward from the spine base
    # These are solid ramps that lean against the spine — self-supporting
    buttress_positions = [-40, -24, -8, 8, 24, 40]
    for i, y_mm in enumerate(buttress_positions):
        side = 1 if i % 2 == 0 else -1
        # Wedge ramp starting at base, rising toward the spine
        cx = mm_to_m(side * 18)
        cy = mm_to_m(y_mm)
        w = mm_to_m(20)
        d = mm_to_m(10)
        h = mm_to_m(12 + i * 2)  # buttresses grow taller toward center
        add_wedge_ramp(bm, cx, cy, w, d, h, t, flip=(side < 0))

    # Cross-beams at the top (horizontal beams are fine — they bridge the spine width)
    add_box(bm, 0, 0, t + spine_h, mm_to_m(35), mm_to_m(2), mm_to_m(2))
    add_box(bm, 0, mm_to_m(20), t + spine_h * 0.7, mm_to_m(25), mm_to_m(2), mm_to_m(2))
    add_box(bm, 0, mm_to_m(-20), t + spine_h * 0.7, mm_to_m(25), mm_to_m(2), mm_to_m(2))

    return bm


def build_v4_splayed_ribcage(seed):
    """Variation 4: Opposing wedge ramp pairs at escalating heights. A ribcage opening."""
    bm = bmesh.new()
    t = mm_to_m(BASE_THICKNESS)

    build_base_tongue_bm(bm, mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), t)

    # Central spine (low ridge)
    add_box(bm, 0, 0, t + mm_to_m(4), mm_to_m(2.5), mm_to_m(70), mm_to_m(4))

    # 4 pairs of opposing wedge ramps — each pair forces pages apart
    rib_configs = [
        # (y_offset_mm, width_mm, depth_mm, peak_height_mm)
        (-30, 55, 20, 8),
        (-10, 65, 22, 12),
        (10,  75, 25, 18),
        (30,  85, 28, 24),
    ]
    for y_off, w, d, h in rib_configs:
        # Right ramp — rises toward +Y
        add_wedge_ramp(bm, mm_to_m(12), mm_to_m(y_off),
                       mm_to_m(w), mm_to_m(d), mm_to_m(h), t, flip=False)
        # Left ramp — rises toward -Y (mirror)
        add_wedge_ramp(bm, mm_to_m(-12), mm_to_m(y_off),
                       mm_to_m(w * 0.75), mm_to_m(d), mm_to_m(h * 0.8), t, flip=True)

    # Vertical connecting struts between ribs
    for i in range(3):
        y = mm_to_m(-25 + i * 20)
        add_box(bm, mm_to_m(18), y, t + mm_to_m(8), mm_to_m(1.5), mm_to_m(1.5), mm_to_m(8))
        add_box(bm, mm_to_m(-14), y, t + mm_to_m(6), mm_to_m(1.5), mm_to_m(1.5), mm_to_m(6))

    return bm


def build_v5_full_eruption(seed):
    """Variation 5: Maximum spread. Dense lattice + stacked wedge ramps + vertical fins."""
    rng = random.Random(seed)
    bm = bmesh.new()
    t = mm_to_m(BASE_THICKNESS)
    sw = mm_to_m(2.5)

    build_base_tongue_bm(bm, mm_to_m(BASE_WIDTH), mm_to_m(BASE_HEIGHT), t)

    # Dense, tall lattice with organic decay
    build_lattice_grid(
        bm,
        width=mm_to_m(100), depth=mm_to_m(80), height=mm_to_m(22),
        cell_size=mm_to_m(8), strut_t=sw, z_base=t,
        seed=seed, remove_ratio=0.25
    )

    # Three tiers of opposing wedge ramps — stacked, escalating
    for tier, (z_off, h, w_scale) in enumerate([
        (0,    mm_to_m(10), 0.7),
        (mm_to_m(10), mm_to_m(14), 0.85),
        (mm_to_m(24), mm_to_m(18), 1.0),
    ]):
        w = mm_to_m(90 * w_scale)
        d = mm_to_m(30)
        add_wedge_ramp(bm, 0, mm_to_m(8 * tier), w, d, h, t + z_off, flip=False)
        add_wedge_ramp(bm, 0, mm_to_m(-8 * tier), w, d, h, t + z_off, flip=True)

    # Chaotic vertical fins (boxes are fully self-supporting)
    for i in range(5):
        x = mm_to_m(rng.uniform(-50, 50))
        y = mm_to_m(rng.uniform(-35, 35))
        h = mm_to_m(rng.uniform(15, 35))
        d = mm_to_m(rng.uniform(8, 18))
        add_box(bm, x, y, t + h / 2, mm_to_m(1.5), d / 2, h / 2)

    return bm


# ============================================================
# Generator dispatch
# ============================================================

BUILDERS = [
    build_v1_minimal_cage,
    build_v2_asymmetric_shelf,
    build_v3_cathedral_arch,
    build_v4_splayed_ribcage,
    build_v5_full_eruption,
]

NAMES = [
    "minimal_cage",
    "asymmetric_shelf",
    "cathedral_arch",
    "splayed_ribcage",
    "full_eruption",
]


def generate_structural_parasite(variation_index, cfg):
    """Generate one Structural Parasite bookmark variation."""
    clear_scene()
    seed = cfg["seeds"][variation_index]
    builder = BUILDERS[variation_index]
    vname = NAMES[variation_index]

    print(f"\n=== Generating Structural Parasite {variation_index + 1}/{cfg['count']} "
          f"— {vname} (seed={seed}) ===")

    # Build the entire form in one bmesh
    bm = builder(seed)

    # Convert to Blender object
    mesh = bpy.data.meshes.new(f"parasite_{vname}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(f"structural_parasite_{variation_index + 1}_{vname}", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Voxel remesh to fuse all parts into a single solid
    mod = obj.modifiers.new(name="Remesh", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = mm_to_m(0.8)
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # Export
    filepath = os.path.join(
        STRUCTURAL_PARASITES_DIR,
        f"structural_parasite_{variation_index + 1}_{vname}.stl"
    )
    export_stl(obj, filepath)
    return filepath


def main():
    """Generate all Structural Parasite variations."""
    cfg = STRUCTURAL_PARASITE_CONFIG
    print(f"\n{'='*60}")
    print(f"THE STRUCTURAL PARASITE — Generating {cfg['count']} variations")
    print(f"{'='*60}")
    print("  1: Minimal Cage — tight, claustrophobic grid")
    print("  2: Asymmetric Shelf — lopsided eruption")
    print("  3: Cathedral Arch — tall spine with buttresses")
    print("  4: Splayed Ribcage — fanning wing pairs")
    print("  5: Full Eruption — maximum chaos\n")

    generated = []
    for i in range(cfg["count"]):
        path = generate_structural_parasite(i, cfg)
        generated.append(path)

    print(f"\n✓ Generated {len(generated)} Structural Parasites")
    for p in generated:
        print(f"  {p}")
    return generated


if __name__ == "__main__":
    main()
