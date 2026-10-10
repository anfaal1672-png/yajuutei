"""屋内の階段・塔屋・屋上（工程 structure / exterior / props）。"""
from __future__ import annotations

from .. import palette as P
from ..voxel import AIR, B, Model
from . import dims as D
from .parts import door, light, stairs

STAIR_MAT = "oak_stairs"
STAIR_SUPPORT = B("oak_planks")


def build_interior_stairs(m: Model) -> None:
    """U字の折り返し階段（x=1..2, z=1..5）。各階: 東の列を北へ2段 → 踊り場 → 西の列を南へ1段 → 上の階。"""
    m.phase = "interior"
    for f in (D.Y_G, D.Y_1F, D.Y_2F, D.Y_3F):
        top = f + 4
        # 上の階の床に穴
        for x, z in [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (2, 4)]:
            m.set(x, top, z, AIR)
        # 1本目（東の列 x=2、北へ上がる）
        m.set(2, f + 1, 4, stairs(STAIR_MAT, "north"))
        m.set(2, f + 2, 3, stairs(STAIR_MAT, "north"))
        # 踊り場（下は空けておく。下の階の踊り場の頭上を 3ブロック確保するため）
        for x in (1, 2):
            for z in (1, 2):
                m.set(x, f + 2, z, STAIR_SUPPORT)
        # 2本目（西の列 x=1、南へ上がる）→ (1, top, 4) の床に着く
        m.set(1, f + 3, 3, stairs(STAIR_MAT, "south"))
        # 階段室の明かり
        light(m, 2, f + 3, 5, 11)


def build_penthouse(m: Model) -> None:
    """塔屋（階段室の上の白い箱。写真③の上部）。"""
    m.phase = "structure"
    y0 = D.Y_ROOF
    m.hollow(0, y0 + 1, 0, 3, y0 + 3, 6, P.PENTHOUSE)
    m.fill(1, y0 + 1, 1, 2, y0 + 3, 5, AIR)
    m.fill(0, D.Y_PH_ROOF, 0, 3, D.Y_PH_ROOF, 6, P.PENTHOUSE_TRIM)
    m.phase = "openings"
    door(m, 1, y0 + 1, 6, "birch_door", "south")
    m.set(3, y0 + 2, 3, P.GLASS)
    m.set(0, y0 + 2, 3, P.GLASS)
    m.phase = "exterior"
    # テレビアンテナ
    m.fill(1, D.Y_PH_ROOF + 1, 1, 1, D.Y_PH_ROOF + 3, 1, B("iron_bars"))
    m.fill(0, D.Y_PH_ROOF + 3, 1, 2, D.Y_PH_ROOF + 3, 1, B("iron_bars"))
    m.set(1, D.Y_PH_ROOF + 4, 1, B("lightning_rod", facing_direction=1, powered_bit=False))


def build_sunroom(m: Model) -> None:
    """屋上の東側のガラス屋根（金属の骨組み＋ポリカーボネート。写真①右上）。2段の片流れ。"""
    m.phase = "exterior"
    y = D.Y_ROOF + 1
    x0, x1 = 4, 8
    back = (1, 4)   # 高い方（北）
    front = (5, 8)  # 低い方（南）
    for x in (x0, x1):
        for z in (back[0], back[1]):
            m.fill(x, y, z, x, y + 2, z, P.SUNROOM_POST)
        for z in (front[1],):
            m.fill(x, y, z, x, y + 1, z, P.SUNROOM_POST)
    m.fill(x0, y + 3, back[0], x1, y + 3, back[1], P.SUNROOM_ROOF)
    m.fill(x0, y + 2, front[0], x1, y + 2, front[1], P.SUNROOM_ROOF)
    # 骨組み（縁）
    for x in range(x0, x1 + 1):
        m.set(x, y + 3, back[0], B("smooth_stone_slab", vhalf="bottom"))
        m.set(x, y + 2, front[1], B("smooth_stone_slab", vhalf="bottom"))


def build_roof_floor(m: Model) -> None:
    """屋上の床のタイル（2×2の市松）。"""
    m.phase = "interior"
    for x in range(1, D.HX1):
        for z in range(1, D.H3_Z1):
            if (x // 2 + z // 2) % 2:
                if m.get(x, D.Y_ROOF, z) == P.ROOF_FLOOR:
                    m.set(x, D.Y_ROOF, z, P.ROOF_FLOOR_ALT)


def build_roof_props(m: Model) -> None:
    """屋上の小物: 日光浴のマット2枚、サンルームのテーブルと椅子、植木鉢、室外機。"""
    m.phase = "props"
    y = D.Y_ROOF + 1
    # マット（青と白のレジャーシート、それぞれ 1×3）
    for z in (7, 8, 9):
        m.set(1, y, z, B("light_blue_carpet"))
        m.set(2, y, z, B("white_carpet"))
    # サンルームの下のテーブルと椅子
    m.set(6, y, 2, B("dark_oak_fence"))
    m.set(6, y + 1, 2, B("light_weighted_pressure_plate"))
    m.set(5, y, 2, stairs("spruce_stairs", "west"))
    m.set(7, y, 2, stairs("spruce_stairs", "east"))
    # 植木鉢
    for x, z in [(8, 9), (5, 1), (3, 9)]:
        m.set(x, y, z, B("decorated_pot", direction=0))
        m.set(x, y + 1, z, B("azalea_leaves", persistent_bit=True, update_bit=False))
    # 室外機
    for x in (6, 7):
        m.set(x, y, 9, B("smooth_quartz", pillar_axis="y"))
        m.set(x, y + 1, 9, B("smooth_quartz_slab", vhalf="bottom"))
    # 夜の明かり
    light(m, 6, y + 1, 6, 10)
    light(m, 2, y + 1, 9, 8)
