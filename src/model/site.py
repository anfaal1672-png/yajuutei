"""敷地・道路・擁壁・塀（工程 site）。"""
from __future__ import annotations

import random

from .. import palette as P
from ..voxel import AIR, B, Model
from . import dims as D


def build_site(m: Model, era: str) -> None:
    m.phase = "site"
    (bx0, by0, bz0), (bx1, by1, bz1) = D.BBOX
    rng = random.Random(810)

    # 地面（範囲全体を草地に。y=0 は元の地面を置き換える）
    m.fill(bx0, 0, bz0, bx1, 0, bz1, P.GRASS)

    # ---- 道路 ----
    m.fill(bx0, 0, D.ROAD_Z0, bx1, 0, D.ROAD_Z1, P.ROAD)
    m.fill(D.XROAD_X0, 0, bz0, D.XROAD_X1, 0, bz1, P.ROAD)
    # 白線とグリーンベルト（前面道路の北側＝敷地側）。交差点の中には引かない
    for x in range(bx0, D.XROAD_X0):
        m.set(x, 1, D.ROAD_Z0, P.GREEN_BELT)
        m.set(x, 1, D.ROAD_Z0 + 1, P.ROAD_LINE)
        m.set(x, 1, D.ROAD_Z1, P.ROAD_LINE)
    for z in list(range(bz0, D.ROAD_Z0)) + list(range(D.ROAD_Z1 + 1, bz1 + 1)):
        m.set(D.XROAD_X0, 1, z, P.ROAD_LINE)
        m.set(D.XROAD_X1, 1, z, P.ROAD_LINE)
    # 敷地前の舗装（ガレージ前）
    m.fill(-16, 0, D.APRON_Z, 24, 0, D.APRON_Z, P.APRON)

    # ---- 野獣邸の敷地（道路より 4ブロック高い） ----
    x0, x1 = D.LOT_X0, D.LOT_X1 - 1
    m.fill(x0, 1, D.LOT_Z0, x1, D.GRADE - 1, D.FRONT_LINE, P.SOIL)
    m.fill(x0, D.GRADE, D.LOT_Z0, x1, D.GRADE, D.FRONT_LINE, P.GRASS)
    # 前面の擁壁（西の細い庭の前）
    m.fill(-2, 1, D.FRONT_LINE, -1, D.GRADE, D.FRONT_LINE, P.CONCRETE)
    # 主屋・増築棟・外階段の部分は掘っておく（あとで建物が入る）
    m.fill(D.HX0, 1, D.HZ0, D.HX1, D.GRADE, D.HZ1, AIR)
    m.fill(D.AX0, 1, D.AZ0, D.SX1, D.GRADE, D.FRONT_LINE, AIR)
    if era == "2001":
        # 前面は道路と同じ高さの駐車スペース（写真③の左に車が見える）
        m.fill(D.AX0, 0, D.AZ0, D.AX1, 0, D.FRONT_LINE, P.APRON)
        m.fill(-1, 1, D.AZ0, -1, D.GRADE, D.FRONT_LINE, P.CONCRETE)  # 西側の擁壁

    # 境界の塀: 西 x=-3、北 z=-4（コンクリートブロック塀）
    m.fill(-3, 1, D.LOT_Z0 - 1, -3, D.GRADE + 1, D.FRONT_LINE, P.BLOCK_WALL)
    m.fill(-3, 1, D.LOT_Z0 - 1, D.LOT_X1, D.GRADE + 1, D.LOT_Z0 - 1, P.BLOCK_WALL)
    m.fill(-3, 1, D.FRONT_LINE, -3, D.GRADE, D.FRONT_LINE, P.CONCRETE)
    # 東 x=12: 主屋の横は古いブロック塀（写真③右）。外階段の横は打ち放しの壁（階段の段に合わせて上がる）
    m.fill(D.LOT_X1, 1, D.LOT_Z0 - 1, D.LOT_X1, D.GRADE + 1, D.HZ1, P.BLOCK_WALL)

    build_east_neighbor(m, rng)
    build_west_neighbor(m)
    build_across(m)


def build_east_neighbor(m: Model, rng: random.Random) -> None:
    """東隣の角地（写真②）: 古い石積みの高い擁壁、竹やツタ。手前の倉庫は無関係なので作らない。"""
    x0, x1, z0, z1 = D.LOT_X1 + 1, 24, -8, D.APRON_Z
    top = 3
    m.fill(x0, 1, z0, x1, top - 1, z1, P.SOIL)
    m.fill(x0, top, z0, x1, top, z1, P.GRASS)
    # 擁壁: 前面道路側（z=20）と交差道路側（x=24）
    for x in range(x0, x1 + 1):
        for y in range(1, top + 1):
            m.set(x, y, z1, rng.choice(P.RETAIN_OLD))
    for z in range(z0, z1 + 1):
        for y in range(1, top + 1):
            m.set(x1, y, z, rng.choice(P.RETAIN_OLD))
    # 擁壁の上に低い笠石
    for x in range(x0, x1 + 1):
        m.set(x, top + 1, z1, B("cobblestone_wall"))
    for z in range(z0, z1):
        m.set(x1, top + 1, z, B("cobblestone_wall"))
    # 古い2階建ての家（雰囲気だけ）
    hx0, hx1, hz0, hz1 = 15, 22, -7, 1
    m.fill(hx0, top + 1, hz0, hx1, top + 7, hz1, P.NEIGHBOR_OLD_WALL)
    m.fill(hx0 + 1, top + 1, hz0 + 1, hx1 - 1, top + 6, hz1 - 1, AIR)
    m.fill(hx0 + 1, top + 4, hz0 + 1, hx1 - 1, top + 4, hz1 - 1, B("spruce_planks"))
    for z in range(hz0 + 2, hz1 - 1, 3):
        for y in (top + 2, top + 6):
            m.set(hx1, y, z, B("glass_pane"))
            m.set(hx0, y, z, B("glass_pane"))
    for x in range(hx0 + 2, hx1 - 1, 3):
        for y in (top + 2, top + 6):
            m.set(x, y, hz1, B("glass_pane"))
    # 切妻屋根（南北方向の棟）
    from .parts import stairs
    ridge = (hx0 + hx1) / 2
    for i in range(0, 5):
        y = top + 8 + i
        xa, xb = hx0 - 1 + i, hx1 + 1 - i
        if xa > xb:
            break
        for z in range(hz0 - 1, hz1 + 2):
            if xa == xb:
                m.set(xa, y, z, B("deepslate_tile_slab", vhalf="bottom"))
            else:
                m.set(xa, y, z, stairs("deepslate_tile_stairs", "east"))
                m.set(xb, y, z, stairs("deepslate_tile_stairs", "west"))
        for z in (hz0, hz1):
            for x in range(xa + 1, xb):
                m.set(x, y, z, P.NEIGHBOR_OLD_WALL)
    _ = ridge


def build_west_neighbor(m: Model) -> None:
    """西隣の白いタイルの建物（写真①左。雰囲気だけ）。"""
    x0, x1, z0, z1 = -14, -5, 1, 18
    h = 14
    m.fill(x0, 1, z0, x1, h, z1, P.NEIGHBOR_WALL)
    m.fill(x0 + 1, 1, z0 + 1, x1 - 1, h - 1, z1 - 1, AIR)
    for y in (4, 8, 12):
        m.fill(x0 + 1, y, z0 + 1, x1 - 1, y, z1 - 1, B("smooth_stone"))
    m.fill(x0, h + 1, z0, x1, h + 1, z1, B("smooth_quartz_slab", vhalf="bottom"))
    m.fill(x0 + 1, h + 1, z0 + 1, x1 - 1, h + 1, z1 - 1, AIR)
    m.fill(x0 + 1, h, z0 + 1, x1 - 1, h, z1 - 1, B("smooth_stone"))
    # 窓（東面と南面）
    for y0 in (1, 5, 9):
        for z in range(z0 + 2, z1 - 1, 3):
            m.fill(x1, y0 + 1, z, x1, y0 + 2, z, B("glass_pane"))
        for x in range(x0 + 2, x1 - 1, 3):
            m.fill(x, y0 + 1, z1, x, y0 + 2, z1, B("glass_pane"))
    # 1階の入口
    m.fill(x1 - 3, 1, z1, x1 - 2, 2, z1, B("glass_pane"))


def build_across(m: Model) -> None:
    """道路の向かい側（低いブロック塀と生垣だけ）。"""
    z = D.ROAD_Z1 + 1
    for x in range(-16, D.XROAD_X0):
        m.set(x, 1, z, P.BLOCK_WALL)
        m.set(x, 1, z + 1, B("oak_leaves", persistent_bit=True, update_bit=False))
        m.set(x, 2, z + 1, B("oak_leaves", persistent_bit=True, update_bit=False))
    for zz in range(-8, D.ROAD_Z0):
        m.set(D.XROAD_X1 + 1, 1, zz, P.BLOCK_WALL)
