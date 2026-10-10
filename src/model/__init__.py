"""建物全体を組み立てる。"""
from __future__ import annotations

from .. import params
from ..voxel import Model
from . import approach, house, planting, rooftop, site
from .rooms import ANNEX_BUILDERS, ROOM_BUILDERS


def build_model(era: str = None, interior: str = None) -> Model:
    era = era or params.ERA
    interior = interior or params.INTERIOR
    m = Model()
    site.build_site(m, era)
    house.build_structure(m, era)
    rooftop.build_penthouse(m)
    house.build_openings(m, era)
    house.build_exterior(m, era)
    approach.build_approach(m, era)
    rooftop.build_sunroom(m)
    rooftop.build_interior_stairs(m)
    rooftop.build_roof_floor(m)

    scenes = {"basement", "living", "kitchen", "genkan", "bath"}
    for name, fn in ROOM_BUILDERS.items():
        if interior == "all" or name in scenes:
            fn(m)
    if era != "2001":
        for name, fn in ANNEX_BUILDERS.items():
            if interior == "all":
                fn(m)
    rooftop.build_roof_props(m)
    planting.build_planting(m, era)
    return m
