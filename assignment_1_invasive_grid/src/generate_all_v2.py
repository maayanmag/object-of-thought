"""
Master generator for The Invasive Grid (v2).
Generates 10 total bookmark parasites:
- 4 Piercers (spikes)
- 3 Bone-Grinders (calcified lumps)
- 3 Structural Parasites (vertical fins)

Run via: /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_all_v2.py
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
        os.path.join(src_dir, "generate_piercers_v2.py"),
        os.path.join(src_dir, "generate_bone_grinders_v2.py"),
        os.path.join(src_dir, "generate_structural_parasites_v2.py"),
    ]

    print("\n" + "="*60)
    print("THE INVASIVE GRID — Bookmark Parasite Generator v2")
    print("="*60)
    print("\nGenerating 10 mutant bookmarks:")
    print("  • 4 Piercers (weaponized spikes)")
    print("  • 3 Bone-Grinders (calcified lumps)")
    print("  • 3 Structural Parasites (vertical fins)")
    print("\nBook dimensions: 210 × 135 × 10 mm (A5 paperback)")
    print("Base bookmark: 40 × 130 × 2 mm (recognizable form)")
    print("\n")

    all_success = True
    for script in scripts:
        if not run_script(script):
            all_success = False
            print(f"❌ Failed: {os.path.basename(script)}")

    if all_success:
        print("\n" + "="*60)
        print("✓ Generation complete! All 10 models ready for 3D printing.")
        print("="*60)

        # Summary
        piercers = os.path.join(PROJECT_ROOT, "models", "piercers")
        bone_grinders = os.path.join(PROJECT_ROOT, "models", "bone_grinders")
        structural = os.path.join(PROJECT_ROOT, "models", "structural_parasites")

        p_count = len([f for f in os.listdir(piercers) if f.endswith(".stl")])
        b_count = len([f for f in os.listdir(bone_grinders) if f.endswith(".stl")])
        s_count = len([f for f in os.listdir(structural) if f.endswith(".stl")])

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
