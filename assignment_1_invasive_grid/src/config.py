"""
Shared configuration for The Invasive Grid project.
All dimensions in millimeters.
Minimum wall: 0.8mm (2× nozzle width for 0.4mm nozzle)
Minimum feature: 0.5mm
"""

import os
import math

# --- Project paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

PIERCERS_DIR = os.path.join(MODELS_DIR, "piercers")
BONE_GRINDERS_DIR = os.path.join(MODELS_DIR, "bone_grinders")
STRUCTURAL_PARASITES_DIR = os.path.join(MODELS_DIR, "structural_parasites")

# --- Book dimensions ---
BOOK_HEIGHT = 210.0
BOOK_WIDTH = 135.0
BOOK_SPINE = 10.0

# --- Shared bookmark base (the vestigial tongue) ---
BASE_WIDTH = 40.0
BASE_HEIGHT = 130.0
BASE_THICKNESS = 2.0

# Shorter base for Bone-Grinders (sits deeper, less protrusion)
BASE_HEIGHT_SHORT = 100.0

# --- Printability constraints ---
NOZZLE_DIAMETER = 0.4
MIN_WALL = 0.8          # 2 perimeters
MIN_TIP_RADIUS = 0.5    # must exceed nozzle diameter
VOXEL_SIZE = 0.002       # 2mm voxels (was 0.8mm — way too dense)

# --- Species 1: The Piercer (4 distinct morphologies) ---
PIERCER_CONFIG = {
    "variants": {
        "sparse_needles": {
            "description": "Few (2-3) long aggressive spikes. Book becomes a pincushion.",
            "spike_count": 3,
            "spike_length_range": (25.0, 35.0),
            "spike_base_radius_range": (2.5, 3.5),
            "spike_tip_radius": 0.6,
            "spike_tilt_range": (5.0, 15.0),
            "seed": 42,
        },
        "dense_cluster": {
            "description": "Many (8-10) short blunt nubs. Fuzzy, textured surface.",
            "spike_count": 8,
            "spike_length_range": (5.0, 10.0),
            "spike_base_radius_range": (2.5, 4.0),
            "spike_tip_radius": 1.2,
            "spike_tilt_range": (15.0, 40.0),
            "seed": 137,
        },
        "spiral_ascent": {
            "description": "5 spikes twist upward in helical pattern. Dynamic, rotational.",
            "spike_count": 5,
            "spike_length_range": (15.0, 22.0),
            "spike_base_radius_range": (2.0, 3.0),
            "spike_tip_radius": 0.6,
            "spike_tilt_range": (10.0, 30.0),
            "seed": 256,
        },
        "asymmetric_eruption": {
            "description": "One massive spike + small satellites. Unbalanced, topples the book.",
            "dominant_spike_length": (30.0, 40.0),
            "dominant_base_radius": (4.0, 5.5),
            "satellite_count": 3,
            "satellite_spike_length": (5.0, 10.0),
            "satellite_base_radius": (1.5, 2.5),
            "spike_tip_radius": 0.6,
            "spike_tilt_range": (5.0, 25.0),
            "seed": 389,
        },
        "tumor_bloom": {
            "description": "Diseased bookmark — aggressive bumpy/tumorous surface with short fat spikes.",
            "large_bump_strength": 8.0,
            "small_bump_strength": 3.0,
            "spike_count": 2,
            "spike_length_range": (8.0, 14.0),
            "spike_base_radius_range": (3.0, 5.0),
            "spike_tip_radius": 1.0,
            "spike_tilt_range": (5.0, 20.0),
            "seed": 512,
        },
    }
}

# --- Species 2: The Bone-Grinder (4 distinct calcification patterns) ---
BONE_GRINDER_CONFIG = {
    "variants": {
        "monolithic": {
            "description": "Single dense lump, off-center weight. Heavy and unbalanced.",
            "count": 1,
            "body_width": 28.0,
            "body_depth": 40.0,
            "height": 10.0,
            "offset_x": 5.0,
            "offset_y": 8.0,
            "displacement_strength": 2.0,
            "seed": 71,
        },
        "scattered_bumps": {
            "description": "5-6 separate calcified nodules. Chaotic, multiple impact zones.",
            "count": 5,
            "body_width": 7.0,
            "body_depth": 9.0,
            "height_range": (4.0, 8.0),
            "scattered": True,
            "displacement_strength": 1.5,
            "seed": 193,
        },
        "ridge_spine": {
            "description": "Continuous raised ridge. Linear corruption along base.",
            "count": 1,
            "body_width": 6.0,
            "body_depth": 80.0,
            "height": 10.0,
            "linear": True,
            "displacement_strength": 1.2,
            "seed": 307,
        },
        "crystalline_shards": {
            "description": "Jagged fragments and sharp edges. Hostile, broken-mineral surface.",
            "count": 4,
            "body_width": 10.0,
            "body_depth": 15.0,
            "height_range": (5.0, 10.0),
            "jagged": True,
            "displacement_strength": 2.5,
            "seed": 421,
        },
        "corroded_surface": {
            "description": "Bookmark-shaped with rough basalt-like surface. Same silhouette, hostile texture.",
            "seed": 550,
        },
        "geological": {
            "description": "Ultra-rough basalt — deep vesicles, sharp crags, volcanic pitting.",
            "seed": 551,
        },
        "brutalist": {
            "description": "Brutalist chunky slab — high peaks, deep grooves, granite fractures.",
            "seed": 552,
        },
        "flint": {
            "description": "Flint-like — sharp jagged edges, abrasive, extreme tactile relief.",
            "seed": 553,
        },
    }
}

# --- Species 3: The Structural Parasite (4 distinct enforcement logics) ---
STRUCTURAL_PARASITE_CONFIG = {
    "variants": {
        "opposing_fins": {
            "description": "Two parallel vertical fins. Symmetric, architectural, rigid.",
            "fin_count": 2,
            "fin_height": 40.0,
            "fin_thickness": 2.0,
            "fin_width": 30.0,
            "opening_angle": 25.0,
            "seed": 99,
        },
        "spiral_twist": {
            "description": "Single fin rotating as it ascends. Dynamic, kinetic energy.",
            "fin_count": 1,
            "fin_height": 45.0,
            "fin_thickness": 2.0,
            "fin_width": 22.0,
            "opening_angle": 30.0,
            "twist_rotation": 120.0,
            "seed": 211,
        },
        "splayed_ribcage": {
            "description": "4 ribs splaying outward. Organic, violent, like broken ribs.",
            "fin_count": 4,
            "fin_height": 35.0,
            "fin_thickness": 2.0,
            "fin_width": 15.0,
            "opening_angle_range": (15.0, 40.0),
            "seed": 337,
        },
        "wedge_ramp": {
            "description": "Single long wedge at shallow angle. Minimalist, unstoppable.",
            "fin_count": 1,
            "fin_height": 30.0,
            "fin_thickness": 3.0,
            "fin_width": 90.0,
            "opening_angle": 15.0,
            "seed": 449,
        },
    }
}

# --- Prime number placement ---
def primes_up_to(n):
    """Sieve of Eratosthenes."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [p for p in range(2, n + 1) if sieve[p]]

TOTAL_PAGES = 80
PRIME_PAGES = primes_up_to(TOTAL_PAGES)

def assign_species():
    """Map each prime page to a species and variation index."""
    primes = PRIME_PAGES
    n = len(primes)
    third = n // 3
    
    piercer_names = list(PIERCER_CONFIG["variants"].keys())
    bone_grinder_names = list(BONE_GRINDER_CONFIG["variants"].keys())
    struct_names = list(STRUCTURAL_PARASITE_CONFIG["variants"].keys())
    
    assignments = []
    for i, page in enumerate(primes):
        if i < third:
            species = "piercer"
            variation_name = piercer_names[i % len(piercer_names)]
        elif i < 2 * third:
            species = "bone_grinder"
            variation_name = bone_grinder_names[(i - third) % len(bone_grinder_names)]
        else:
            species = "structural_parasite"
            variation_name = struct_names[(i - 2 * third) % len(struct_names)]
        assignments.append({
            "page": page,
            "species": species,
            "variation": variation_name,
            "phase": "infection" if species == "piercer"
                     else "colonization" if species == "bone_grinder"
                     else "transformation"
        })
    return assignments

COLONIZATION_MAP = assign_species()
