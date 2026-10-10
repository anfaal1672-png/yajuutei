"""外階段・玄関ポーチ・門（工程 exterior）。

道路（立つ高さ 1）から玄関ポーチ（立つ高さ 4.5）まで、半ブロックずつ上がる階段にする。
写真①の約16段を 7段（＋2001年版は門の踊り場）で表現（docs/assumptions.md A-06）。
"""
from __future__ import annotations

from .. import palette as P
from ..voxel import AIR, B, Model
from . import dims as D
from .parts import door, light


def _half_step(m: Model, x0: int, x1: int, z: int, surface2: int, bottom, top, full) -> None:
    """立つ高さ surface2/2 の段を置く（下は打ち放しで埋める）。"""
    h = surface2 / 2
    y = int(h - 0.5) if surface2 % 2 else int(h) - 1
    for x in range(x0, x1 + 1):
        if surface2 % 2:  # x.5 → 下付きハーフブロック
            m.set(x, y, z, bottom)
        else:             # x.0 → 上付きハーフブロック（2001年の踊り場は普通のブロック）
            m.set(x, y, z, top)
        for yy in range(1, y):
            m.set(x, yy, z, P.CONCRETE_DARK)
        for yy in range(y + 1, y + 4):
            if m.get(x, yy, z).name not in ("air",):
                pass
            m.set(x, yy, z, AIR)
    _ = full


def build_approach(m: Model, era: str) -> None:
    m.phase = "exterior"
    sx0, sx1 = D.SX0, D.SX1
    if era == "2001":
        # 写真③: 小口タイル（ベージュ）の階段 → 門扉の踊り場 → グレーの階段 → 玄関ポーチ
        steps = [(19, 3), (18, 4), (17, 5)]
        for z, s2 in steps:
            _half_step(m, sx0, sx1, z, s2, P.OLD_STAIR_SLAB, P.OLD_STAIR_SLAB_TOP, None)
        # 踊り場（立つ高さ 3）: 門扉は普通のブロックの上に立てる
        for x in range(sx0, sx1 + 1):
            m.fill(x, 1, 16, x, 2, 16, P.CONCRETE_DARK)
            m.set(x, 2, 16, P.PORCH_FLOOR)
        door(m, sx0, 3, 16, P.DOOR_GATE, "south", hinge=False)
        door(m, sx1, 3, 16, P.DOOR_GATE, "south", hinge=True)
        for z, s2 in [(15, 7), (14, 8), (13, 9)]:
            _half_step(m, sx0, sx1, z, s2, P.OLD_STAIR_GRAY_SLAB, P.OLD_STAIR_GRAY_SLAB_TOP, None)
        # 階段の西側の袖壁（打ち放し）と門柱
        wx = sx0 - 1
        for z in range(13, 20):
            top = 2 if z >= 17 else 5
            m.fill(wx, 1, z, wx, top, z, P.CONCRETE)
        m.fill(wx, 1, 16, wx, 5, 16, P.CONCRETE)
        m.set(wx, 3, 17, B("lantern", hanging=False))  # 門柱の足元灯
    else:
        # 写真①: こげ茶のタイルの階段が一直線に上がる
        for i, z in enumerate(range(D.STAIR_Z_BOTTOM, D.STAIR_Z_TOP - 1, -1)):
            _half_step(m, sx0, sx1, z, 3 + i, P.STAIR_TILE_SLAB, P.STAIR_TILE_SLAB_TOP, None)
    # 東側の境界の打ち放しの壁（段に沿って上がり、手すりの高さ）
    for z in range(D.STAIR_Z_TOP, D.STAIR_Z_BOTTOM + 1):
        surf = 1 + (D.STAIR_Z_BOTTOM - z + 1) * 0.5
        top = int(surf) + 1
        m.fill(D.LOT_X1, 1, z, D.LOT_X1, top, z, P.CONCRETE)
    # 玄関ポーチの庇（ポーチの上に 2ブロック張り出す。上は 2階のバルコニー）
    m.fill(sx0, D.Y_2F, D.PORCH_Z1 + 1, sx1, D.Y_2F, D.PORCH_Z1 + 2, P.CONCRETE)
    # ポーチの照明（ダウンライト）
    m.set(sx0, D.Y_2F - 1, D.PORCH_Z0 + 1, B("lantern", hanging=True))
    light(m, sx1, D.Y_2F - 1, D.PORCH_Z0 + 1, 12)
