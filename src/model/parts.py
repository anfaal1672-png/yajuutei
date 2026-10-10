"""部品を置く関数（階段・扉・木・照明など）。統合版のブロック状態の書き方はここに閉じ込める。

向きの書き方（blocks_bedrock.py の出典を参照）:
  階段 weirdo_direction: 0=東 1=西 2=南 3=北（その方向へ上がる＝背の高い側）
  扉   minecraft:cardinal_direction: south/west/north/east
"""
from __future__ import annotations

import math
import random

from ..voxel import B, Block, Model

WEIRDO = {"east": 0, "west": 1, "south": 2, "north": 3}
OPPOSITE = {"east": "west", "west": "east", "north": "south", "south": "north"}


def stairs(name: str, ascend: str, upside_down: bool = False) -> Block:
    return B(name, weirdo_direction=WEIRDO[ascend], upside_down_bit=upside_down)


def slab(name: str, top: bool = False) -> Block:
    return B(name, vhalf="top" if top else "bottom")


def door(m: Model, x: int, y: int, z: int, name: str, facing: str, hinge: bool = False) -> None:
    """扉（下半分 y、上半分 y+1）。"""
    m.set(x, y, z, B(name, cardinal=facing, door_hinge_bit=hinge, open_bit=False, upper_block_bit=False))
    m.set(x, y + 1, z, B(name, cardinal=facing, door_hinge_bit=hinge, open_bit=False, upper_block_bit=True))


def leaves(kind: str = "oak") -> Block:
    return B(f"{kind}_leaves", persistent_bit=True, update_bit=False)


def log(kind: str = "oak", axis: str = "y") -> Block:
    return B(f"{kind}_log", pillar_axis=axis)


def conifer(m: Model, x: int, y: int, z: int, height: int, rng: random.Random, kind: str = "spruce") -> None:
    """細長い針葉樹（レイランディ系）。y は根元の地面の1つ上。"""
    m.fill(x, y, z, x, y + height - 2, z, log(kind))
    for dy in range(2, height + 1):
        yy = y + dy
        frac = (dy - 2) / max(1, height - 2)
        r = 1.6 * (1 - frac) + 0.6
        ir = int(math.ceil(r))
        for dx in range(-ir, ir + 1):
            for dz in range(-ir, ir + 1):
                if dx == 0 and dz == 0 and dy < height - 1:
                    continue
                if dx * dx + dz * dz <= r * r + rng.random() * 0.6:
                    if m.get(x + dx, yy, z + dz).name == "air":
                        m.set(x + dx, yy, z + dz, leaves(kind))
    m.set(x, y + height, z, leaves(kind))


def broadleaf(m: Model, x: int, y: int, z: int, height: int, radius: float, rng: random.Random,
              kind: str = "oak") -> None:
    m.fill(x, y, z, x, y + height - 1, z, log(kind))
    cy = y + height - 1
    ir = int(math.ceil(radius))
    for dx in range(-ir, ir + 1):
        for dy in range(-ir, ir + 1):
            for dz in range(-ir, ir + 1):
                d = (dx * dx + (dy * 1.4) ** 2 + dz * dz) ** 0.5
                if d <= radius - rng.random() * 0.7:
                    p = (x + dx, cy + dy, z + dz)
                    if m.get(*p).name == "air":
                        m.set(*p, leaves(kind))


def bamboo_stalk(m: Model, x: int, y: int, z: int, height: int) -> None:
    for i in range(height):
        top = i >= height - 2
        m.set(x, y + i, z, B("bamboo", age_bit=False,
                             bamboo_leaf_size="large_leaves" if i == height - 1 else ("small_leaves" if top else "no_leaves"),
                             bamboo_stalk_thickness="thick"))


def railing(m: Model, cells, y: int, cap: bool = True) -> None:
    """縦格子の手すり（鉄格子＋上に笠木のハーフブロック）。"""
    for x, z in cells:
        m.set(x, y, z, B("iron_bars"))
        if cap:
            m.set(x, y + 1, z, B("smooth_stone_slab", vhalf="bottom"))


def light(m: Model, x: int, y: int, z: int, level: int = 12) -> None:
    if m.get(x, y, z).name == "air":
        m.set(x, y, z, B(f"light_block_{level}"))
