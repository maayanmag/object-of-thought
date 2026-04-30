"""
Master generator for The Invasive Grid (v3 — Qualitative Diversity).
Generates 10 distinct bookmark parasites with maximum conceptual variance:
- 4 Piercers: Sparse Needles, Dense Cluster, Spiral Ascent, Asymmetric Eruption
- 3 Bone-Grinders: Monolithic, Scattered Bumps, Ridge Spine, Crystalline Shards
- 3 Structural Parasites: Opposing Fins, Spiral Twist, Splayed Ribcage, Wedge Ramp

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_all_v3.py
"""

import subprocess
import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)  # up to assignment folder

def run_script(script_path):
    """Run a Blender Python script in background mode."""
    cmd = [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "--background",
        "--python",
        script_path
    ]
    print(f"\n{'='*60}")
    print(f"Running: {os.path.basename(script_path)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0


def main():
    src_dir = os.path.join(PROJECT_ROOT, "src")
    scripts = [
        os.path.join(src_dir, "generate_piercers_v3.py"),
        os.path.join(src_dir, "generate_bone_grinders_v3.py"),
        os.path.join(src_dir, "generate_structural_parasites_v3.py"),
    ]

    print("\n" + "="*60)
    print("THE INVASIVE GRID — v3: Qualitative Diversity")
    print("="*60)
    print("\nGenerating 10 distinct mutant bookmarks:")
    print("\nPIERCERS (4 spike morphologies):")
    print("  • Sparse Needles: Few, long, thin, aggressive")
    print("  • Dense Cluster: Many, short, blunt, fuzzy")
    print("  • Spiral Ascent: Helical twist, dynamic")
    print("  • Asymmetric Eruption: One massive spike + satellites")
    print("\nBONE-GRINDERS (4 calcification patterns):")
    print("  • Monolithic: Single heavy lump, off-center")
    print("  • Scattered Bumps: 5-7 separate nodules, chaotic")
    print("  • Ridge Spine: Linear raised ridge, continuous")
    print("  • Crystalline Shards: Jagged fragments, hostile")
    print("\nSTRUCTURAL PARASITES (4 enforcement logics):")
    print("  • Opposing Fins: Two parallel fins, symmetric")
    print("  • Spiral Twist: Single fin rotating, kinetic")
    print("  • Splayed Ribcage: Multiple ribs at angles, violent")
    print("  • Wedge Ramp: Single long wedge, relentless")
    print("\n")

    all_success = True
    for script in scripts:
        if not run_script(script):
            all_success = False
            print(f"❌ Failed: {os.path.basename(script)}")

    if all_success:
        print("\n" + "="*60)
        print("✓ Generation complete! 10 models ready for 3D printing.")
        print("="*60)

        # Summary
        piercers = os.path.join(PROJECT_ROOT, "models", "piercers")
        bone_grinders = os.path.join(PROJECT_ROOT, "models", "bone_grinders")
        structural = os.path.join(PROJECT_ROOT, "models", "structural_parasites")

        p_count = len([f for f in os.listdir(piercers) if f.endswith(".stl")]) if os.path.exists(piercers) else 0
        b_count = len([f for f in os.listdir(bone_grinders) if f.endswith(".stl")]) if os.path.exists(bone_grinders) else 0
        s_count = len([f for f in os.listdir(structural) if f.endswith(".stl")]) if os.path.exists(structural) else 0

        print(f"\nSummary:")
        print(f"  Piercers: {p_count} STLs")
        print(f"  Bone-Grinders: {b_count} STLs")
        print(f"  Structural Parasites: {s_count} STLs")
        print(f"  TOTAL: {p_count + b_count + s_count} models")
    else:
        print("\n❌ Generation failed. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
