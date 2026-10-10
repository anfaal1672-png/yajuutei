"""確認用の画像を描く（各階の平面図、写真と同じアングルの透視図）。

ゲームの見た目とは違う簡易描画（ブロックごとの平均色＋面の明暗）。形と配置・色調の確認用。
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw

from .connections import connections, is_connectable
from .shapes import is_opaque_cube, kind
from .voxel import Block, Model

COLORS: Dict[str, Tuple[int, int, int]] = {
    "grass_block": (98, 150, 60), "dirt": (134, 96, 67), "smooth_stone": (166, 166, 164),
    "smooth_stone_slab": (166, 166, 164), "light_gray_terracotta": (135, 107, 98),
    "brown_terracotta": (77, 51, 36), "light_gray_concrete": (125, 125, 115), "gray_concrete": (62, 66, 70),
    "black_concrete": (12, 14, 18), "white_concrete": (207, 213, 214), "smooth_quartz": (236, 230, 223),
    "smooth_quartz_slab": (236, 230, 223), "smooth_quartz_stairs": (236, 230, 223),
    "white_concrete_powder": (225, 227, 227), "stone_bricks": (122, 121, 122), "mossy_cobblestone": (104, 114, 88),
    "cobblestone": (128, 127, 128), "tuff": (108, 109, 102), "mossy_stone_bricks": (115, 121, 105),
    "cobblestone_wall": (128, 127, 128), "mangrove_fence": (125, 56, 48), "glass_pane": (120, 150, 168),
    "white_stained_glass_pane": (215, 222, 224), "white_stained_glass": (226, 230, 230), "glass": (175, 205, 214),
    "iron_bars": (96, 98, 100), "mud_brick_slab": (137, 104, 79), "mud_bricks": (137, 104, 79),
    "smooth_sandstone": (223, 214, 170), "smooth_sandstone_slab": (223, 214, 170), "polished_andesite": (132, 135, 134),
    "polished_andesite_slab": (132, 135, 134), "deepslate_tile_stairs": (58, 58, 60), "deepslate_tile_slab": (58, 58, 60),
    "deepslate_tiles": (58, 58, 60), "light_gray_stained_glass": (190, 196, 200), "iron_chain": (70, 74, 84),
    "oak_planks": (162, 130, 78), "birch_planks": (192, 175, 121), "dark_oak_planks": (66, 43, 20),
    "spruce_planks": (114, 84, 48), "oak_stairs": (162, 130, 78), "spruce_stairs": (114, 84, 48),
    "dark_oak_slab": (66, 43, 20), "spruce_slab": (114, 84, 48), "bamboo_mosaic": (190, 170, 78),
    "bookshelf": (117, 94, 59), "barrel": (134, 100, 58), "white_wool": (233, 236, 236),
    "light_blue_carpet": (58, 175, 217), "white_carpet": (233, 236, 236), "brown_carpet": (114, 71, 40),
    "red_carpet": (160, 39, 34), "gray_carpet": (62, 68, 71), "light_gray_carpet": (142, 142, 134),
    "cyan_carpet": (40, 160, 140), "smoker": (90, 85, 80), "iron_block": (220, 220, 220), "cauldron": (74, 73, 74),
    "water": (63, 118, 228), "sea_lantern": (190, 210, 200), "lantern": (250, 190, 90), "brown_candle": (114, 71, 40),
    "light_weighted_pressure_plate": (246, 208, 61), "flower_pot": (124, 68, 53), "decorated_pot": (150, 80, 60),
    "azalea_leaves": (90, 115, 44), "cherry_leaves": (229, 172, 194), "oak_leaves": (60, 110, 34),
    "spruce_leaves": (48, 78, 50), "jungle_leaves": (60, 120, 35), "birch_leaves": (110, 140, 70), "dark_oak_leaves": (55, 90, 30), "spruce_log": (58, 37, 16), "oak_log": (109, 85, 50), "bamboo": (95, 135, 35),
    "vine": (55, 100, 30), "short_grass": (90, 140, 50), "fern": (80, 125, 45), "azalea": (100, 125, 50),
    "polished_blackstone_stairs": (53, 48, 56), "polished_blackstone_slab": (53, 48, 56), "anvil": (68, 68, 68),
    "grindstone": (142, 142, 142), "lightning_rod": (190, 110, 80), "lever": (110, 100, 90),
    "stone_button": (130, 130, 130), "birch_door": (220, 210, 170), "iron_door": (190, 192, 194),
    "dark_oak_door": (75, 50, 25), "dark_oak_fence": (66, 43, 20), "stripped_mangrove_log": (119, 54, 47), "smooth_stone_stairs": (166, 166, 164),
}


def color_of(b: Block) -> Tuple[int, int, int]:
    if b.name in COLORS:
        return COLORS[b.name]
    h = sum(map(ord, b.name))
    return (100 + h % 100, 100 + (h * 7) % 100, 100 + (h * 13) % 100)


def boxes(m: Model, p, b: Block) -> List[Tuple[float, ...]]:
    k = kind(b)
    n = b.name
    if n.startswith("light_block") or n == "air":
        return []
    if k == "full":
        if n == "water":
            return [(0, 0, 0, 1, 0.875, 1)]
        if n in ("lantern",):
            return [(0.3, 0.1, 0.3, 0.7, 0.6, 0.7)]
        if n in ("decorated_pot",):
            return [(0.15, 0, 0.15, 0.85, 0.9, 0.85)]
        if n in ("flower_pot",):
            return [(0.3, 0, 0.3, 0.7, 0.4, 0.7)]
        if n in ("grindstone", "anvil"):
            return [(0.15, 0, 0.15, 0.85, 0.9, 0.85)]
        if n == "lightning_rod":
            f = b.state("facing_direction", 1)
            return [(0.4, 0, 0.4, 0.6, 1, 0.6)] if f in (0, 1) else [(0.4, 0.4, 0.2, 0.6, 0.6, 1)]
        return [(0, 0, 0, 1, 1, 1)]
    if k == "none":
        if n in ("short_grass", "fern", "azalea", "tall_grass", "large_fern"):
            return [(0.2, 0, 0.2, 0.8, 0.7, 0.8)]
        if n == "vine":
            bits = b.state("vine_direction_bits", 0)
            out = []
            if bits & 4:
                out.append((0, 0, 0, 1, 1, 0.06))
            if bits & 1:
                out.append((0, 0, 0.94, 1, 1, 1))
            if bits & 2:
                out.append((0, 0, 0, 0.06, 1, 1))
            if bits & 8:
                out.append((0.94, 0, 0, 1, 1, 1))
            return out
        if n == "iron_chain":
            return [(0.42, 0, 0.42, 0.58, 1, 0.58)]
        if n == "lantern":
            return [(0.3, 0.2, 0.3, 0.7, 0.75, 0.7)]
        if n.endswith("candle"):
            return [(0.4, 0, 0.4, 0.6, 0.4, 0.6)]
        return [(0.4, 0.4, 0.4, 0.6, 0.6, 0.6)]
    if k == "carpet":
        return [(0, 0, 0, 1, 0.07, 1)]
    if k == "slab":
        return [(0, 0.5, 0, 1, 1, 1)] if b.state("minecraft:vertical_half") == "top" else [(0, 0, 0, 1, 0.5, 1)]
    if k == "stairs":
        d = b.state("weirdo_direction", 0)
        up = b.state("upside_down_bit", False)
        base = (0, 0.5, 0, 1, 1, 1) if up else (0, 0, 0, 1, 0.5, 1)
        y0, y1 = (0, 0.5) if up else (0.5, 1)
        half = {0: (0.5, y0, 0, 1, y1, 1), 1: (0, y0, 0, 0.5, y1, 1),
                2: (0, y0, 0.5, 1, y1, 1), 3: (0, y0, 0, 1, y1, 0.5)}[d]
        return [base, half]
    if k == "door":
        f = b.state("minecraft:cardinal_direction", "south")
        if f in ("south", "north"):
            return [(0, 0, 0.41, 1, 1, 0.59)]
        return [(0.41, 0, 0, 0.59, 1, 1)]
    if k == "trapdoor":
        return [(0, 0.81, 0, 1, 1, 1)] if b.state("upside_down_bit") else [(0, 0, 0, 1, 0.19, 1)]
    if k in ("pane", "fence", "post"):
        t = 0.0625 if k == "pane" else 0.125
        if k == "post":
            return [(0.35, 0, 0.35, 0.65, 1, 0.65)]
        out = [(0.5 - t, 0, 0.5 - t, 0.5 + t, 1, 0.5 + t)]
        if is_connectable(b):
            c = connections(m, p, b)
            y0, y1 = (0, 1) if k == "pane" else (0.4, 0.9)
            if c["east"]:
                out.append((0.5, y0, 0.5 - t, 1, y1, 0.5 + t))
            if c["west"]:
                out.append((0, y0, 0.5 - t, 0.5, y1, 0.5 + t))
            if c["south"]:
                out.append((0.5 - t, y0, 0.5, 0.5 + t, y1, 1))
            if c["north"]:
                out.append((0.5 - t, y0, 0, 0.5 + t, y1, 0.5))
        return out
    return [(0, 0, 0, 1, 1, 1)]


FACES = [
    ((1, 0, 0), lambda b: [(b[3], b[1], b[2]), (b[3], b[4], b[2]), (b[3], b[4], b[5]), (b[3], b[1], b[5])], 0.78),
    ((-1, 0, 0), lambda b: [(b[0], b[1], b[2]), (b[0], b[1], b[5]), (b[0], b[4], b[5]), (b[0], b[4], b[2])], 0.62),
    ((0, 1, 0), lambda b: [(b[0], b[4], b[2]), (b[0], b[4], b[5]), (b[3], b[4], b[5]), (b[3], b[4], b[2])], 1.0),
    ((0, -1, 0), lambda b: [(b[0], b[1], b[2]), (b[3], b[1], b[2]), (b[3], b[1], b[5]), (b[0], b[1], b[5])], 0.45),
    ((0, 0, 1), lambda b: [(b[0], b[1], b[5]), (b[3], b[1], b[5]), (b[3], b[4], b[5]), (b[0], b[4], b[5])], 0.88),
    ((0, 0, -1), lambda b: [(b[0], b[1], b[2]), (b[0], b[4], b[2]), (b[3], b[4], b[2]), (b[3], b[1], b[2])], 0.55),
]


class Camera:
    def __init__(self, pos, target, fov_v=60.0, size=(900, 1200)):
        self.pos = pos
        self.w, self.h = size
        fx, fy, fz = (target[i] - pos[i] for i in range(3))
        n = math.sqrt(fx * fx + fy * fy + fz * fz)
        self.f = (fx / n, fy / n, fz / n)
        up = (0, 1, 0)
        r = (self.f[1] * up[2] - self.f[2] * up[1], self.f[2] * up[0] - self.f[0] * up[2],
             self.f[0] * up[1] - self.f[1] * up[0])
        rn = math.sqrt(sum(c * c for c in r))
        self.r = tuple(c / rn for c in r)
        self.u = (self.r[1] * self.f[2] - self.r[2] * self.f[1], self.r[2] * self.f[0] - self.r[0] * self.f[2],
                  self.r[0] * self.f[1] - self.r[1] * self.f[0])
        self.focal = (self.h / 2) / math.tan(math.radians(fov_v) / 2)

    def project(self, p):
        d = (p[0] - self.pos[0], p[1] - self.pos[1], p[2] - self.pos[2])
        z = d[0] * self.f[0] + d[1] * self.f[1] + d[2] * self.f[2]
        if z < 0.05:
            return None
        x = d[0] * self.r[0] + d[1] * self.r[1] + d[2] * self.r[2]
        y = d[0] * self.u[0] + d[1] * self.u[1] + d[2] * self.u[2]
        return (self.w / 2 + self.focal * x / z, self.h / 2 - self.focal * y / z), z


def render_perspective(m: Model, cam: Camera, path: str, sky=(176, 204, 232)) -> None:
    img = Image.new("RGB", (cam.w, cam.h), sky)
    draw = ImageDraw.Draw(img)
    polys = []
    blocks = m.blocks
    for p, b in blocks.items():
        if b.name == "air":
            continue
        bxs = boxes(m, p, b)
        if not bxs:
            continue
        base = color_of(b)
        for bx in bxs:
            for (nx, ny, nz), fn, shade in FACES:
                # 隣が不透明な立方体で、面がブロックの境界にあるなら描かない
                on_edge = ((nx == 1 and bx[3] == 1) or (nx == -1 and bx[0] == 0) or (ny == 1 and bx[4] == 1) or
                           (ny == -1 and bx[1] == 0) or (nz == 1 and bx[5] == 1) or (nz == -1 and bx[2] == 0))
                if on_edge:
                    nb = blocks.get((p[0] + nx, p[1] + ny, p[2] + nz))
                    if nb is not None and is_opaque_cube(nb):
                        continue
                pts = [(p[0] + a, p[1] + c, p[2] + e) for a, c, e in fn(bx)]
                cx = sum(q[0] for q in pts) / 4
                cy = sum(q[1] for q in pts) / 4
                cz = sum(q[2] for q in pts) / 4
                vx, vy, vz = cam.pos[0] - cx, cam.pos[1] - cy, cam.pos[2] - cz
                if vx * nx + vy * ny + vz * nz <= 0:
                    continue
                proj = [cam.project(q) for q in pts]
                if any(q is None for q in proj):
                    continue
                dist = vx * vx + vy * vy + vz * vz
                col = tuple(int(c * shade) for c in base)
                polys.append((dist, [q[0] for q in proj], col))
    polys.sort(key=lambda t: -t[0])
    for _, pts, col in polys:
        draw.polygon(pts, fill=col, outline=tuple(max(0, c - 18) for c in col))
    img.save(path)


PLAN_CHARS = {
    "wall": "#", "window": "=", "door": "D", "stair": "^", "floor": ".", "furn": "o", "void": " ",
}


def plan_char(m: Model, x: int, f: int, z: int) -> str:
    """平面図の1マス: 床の上（f+1, f+2）を見て記号にする。"""
    b1 = m.get(x, f + 1, z)
    b2 = m.get(x, f + 2, z)
    fl = m.get(x, f, z)
    k1, k2 = kind(b1), kind(b2)
    if k1 == "door":
        return "D"
    if "glass" in b2.name or "glass" in b1.name:
        return "="
    if k1 == "stairs" or k2 == "stairs":
        return "^"
    if k1 == "full" and k2 == "full" and b1.name not in ("lantern",):
        return "#"
    if k1 in ("fence", "pane") and k2 in ("fence", "pane", "none"):
        return "|"
    if k1 in ("full", "slab", "stairs") or b1.name in ("decorated_pot", "cauldron", "anvil", "grindstone", "water"):
        return "o"
    if fl.name == "air" and b1.name == "air":
        return " "
    return "."


def render_plan_png(m: Model, f: int, x0: int, z0: int, x1: int, z1: int, path: str, cell: int = 24) -> None:
    w, h = (x1 - x0 + 1) * cell, (z1 - z0 + 1) * cell
    img = Image.new("RGB", (w, h), (245, 245, 240))
    d = ImageDraw.Draw(img)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            px, pz = (x - x0) * cell, (z - z0) * cell
            top = None
            for y in (f + 2, f + 1, f):
                b = m.get(x, y, z)
                if b.name != "air" and not b.name.startswith("light_block"):
                    top = b
                    break
            if top is None:
                continue
            col = color_of(top)
            d.rectangle([px, pz, px + cell - 1, pz + cell - 1], fill=col, outline=(200, 200, 195))
            ch = plan_char(m, x, f, z)
            if ch in "#=D^|":
                d.text((px + cell // 3, pz + cell // 5), ch, fill=(255, 255, 255) if sum(col) < 380 else (0, 0, 0))
    img.save(path)
