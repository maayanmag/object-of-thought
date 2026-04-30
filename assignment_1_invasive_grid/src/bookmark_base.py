"""
Shared bookmark base generator — the vestigial tongue.
All species inherit this flat insertion body.
Run inside Blender Python context.
"""

import bpy
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import create_cube, mm_to_m


def create_base_tongue(width=40.0, height=130.0, thickness=2.0, name="bookmark_base"):
    """
    Create the flat bookmark tongue that slides between pages.

    The tongue is a simple rectangular slab — the bookmark's
    vestigial original form, before mutation.

    Args:
        width: mm (across the page, X axis)
        height: mm (along the page, Y axis)  
        thickness: mm (Z axis — thin enough to slip between pages)
        name: object name

    Returns:
        Blender object (mesh)
    """
    # Create a flat box centered at origin, bottom face at Z=0
    obj = create_cube(
        name=name,
        size_x=width,
        size_y=height,
        size_z=thickness,
        location=(0, 0, thickness / 2.0)
    )
    return obj
