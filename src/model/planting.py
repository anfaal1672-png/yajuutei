"""植栽（工程 planting）: 東隣の竹・針葉樹（写真②③）、裏庭の低木、擁壁のツタ。"""
from __future__ import annotations

import random

from ..voxel import B, Model
from . import dims as D
from .parts import bamboo_stalk, broadleaf, conifer, leaves


def build_planting(m: Model, era: str) -> None:
    m.phase = "planting"
    rng = random.Random(1919)
    top = 3  # 東隣の地盤面
    # 東隣: 外階段の横に高い針葉樹と広葉樹（写真③右）
    conifer(m, 12, top + 1, 16, 9, rng)
    broadleaf(m, 13, top + 1, 9, 5, 2.2, rng)
    # 東隣: 擁壁の上の竹やぶと茂み（写真②: 擁壁の上から葉が垂れ下がる）
    for x in range(13, 24):
        for z in range(4, 20):
            near_wall = z >= 17 or x >= 21
            if m.get(x, top + 1, z).name != "air" or m.get(x, top, z).name != "grass_block":
                continue
            r = rng.random()
            if near_wall and r < 0.55:
                h = rng.randint(1, 2)
                for y in range(top + 1, top + 1 + h):
                    m.set(x, y, z, leaves(rng.choice(["oak", "jungle", "azalea"])))
            elif r < 0.12:
                bamboo_stalk(m, x, top + 1, z, rng.randint(4, 7))
    # 擁壁を垂れるツタ（道路側の面）
    for x in range(D.LOT_X1 + 1, 24):
        if rng.random() < 0.7:
            for y in range(rng.randint(1, 2), 4):
                m.set(x, y, D.APRON_Z + 1, B("vine", vine_direction_bits=4))
    for z in range(-6, 20):
        if rng.random() < 0.6:
            for y in range(rng.randint(1, 2), 4):
                m.set(D.XROAD_X0, y, z, B("vine", vine_direction_bits=2))
    # 野獣邸の裏庭と西の細い庭: 低木と草
    for x in range(-2, D.LOT_X1):
        for z in range(D.LOT_Z0, 0):
            r = rng.random()
            if r < 0.12:
                m.set(x, D.GRADE + 1, z, B("azalea"))
            elif r < 0.35:
                m.set(x, D.GRADE + 1, z, B("short_grass"))
    for z in range(0, 19):
        for x in (-2, -1):
            if m.get(x, D.GRADE, z).name != "grass_block" or m.get(x, D.GRADE + 1, z).name != "air":
                continue
            r = rng.random()
            if r < 0.15:
                m.set(x, D.GRADE + 1, z, leaves("oak"))
            elif r < 0.4:
                m.set(x, D.GRADE + 1, z, B("fern"))
    conifer(m, -2, D.GRADE + 1, -2, 8, rng)
    conifer(m, 8, D.GRADE + 1, -2, 7, rng)
