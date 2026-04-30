"""
Master generator for The Invasive Grid.
Runs all three species generators and creates the colonization map.

Run via:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python generate_all.py
"""

import bpy
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import COLONIZATION_MAP, DATA_DIR, MODELS_DIR

from generate_piercers import main as generate_piercers
from generate_bone_grinders import main as generate_bone_grinders
from generate_structural_parasites import main as generate_structural_parasites


def write_colonization_map():
    """Write the prime page → species → variation mapping as JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, "prime_colonization.json")

    output = {
        "title": "The Invasive Grid — Colonization Protocol",
        "description": (
            "Each prime-numbered page is colonized by a mutant bookmark species. "
            "The sequence follows an evolutionary arc: "
            "infection (Piercers) → colonization (Bone-Grinders) → transformation (Structural Parasites)."
        ),
        "placements": COLONIZATION_MAP,
        "summary": {
            "total_specimens": len(COLONIZATION_MAP),
            "species_distribution": {}
        }
    }

    # Count per species
    for entry in COLONIZATION_MAP:
        sp = entry["species"]
        output["summary"]["species_distribution"][sp] = (
            output["summary"]["species_distribution"].get(sp, 0) + 1
        )

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Colonization map written to: {filepath}")
    print(f"  Total placements: {len(COLONIZATION_MAP)}")
    for sp, count in output["summary"]["species_distribution"].items():
        print(f"  {sp}: {count}")

    return filepath


def count_stls():
    """Count generated STL files."""
    count = 0
    for root, dirs, files in os.walk(MODELS_DIR):
        for f in files:
            if f.endswith(".stl"):
                count += 1
    return count


def main():
    print("\n" + "=" * 60)
    print("THE INVASIVE GRID — Full Generation Pipeline")
    print("=" * 60)
    print("The bookmark was the most obedient object in the library.")
    print("Now it has teeth.\n")

    # Generate all species
    piercer_paths = generate_piercers()
    bone_grinder_paths = generate_bone_grinders()
    parasite_paths = generate_structural_parasites()

    # Write placement map
    map_path = write_colonization_map()

    # Summary
    total_stls = count_stls()
    print("\n" + "=" * 60)
    print(f"GENERATION COMPLETE")
    print(f"  STL files: {total_stls}")
    print(f"  Piercers: {len(piercer_paths)}")
    print(f"  Bone-Grinders: {len(bone_grinder_paths)}")
    print(f"  Structural Parasites: {len(parasite_paths)}")
    print(f"  Colonization map: {map_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
