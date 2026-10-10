"""地下階: 地下室と物置。主屋の下は敷地の地盤より低いので「地下室」になる。確度C。"""
from __future__ import annotations

from ... import palette as P
from ...voxel import B, Model
from .. import dims as D
from ..parts import light, stairs

F = D.Y_G
Y = F + 1


def build(m: Model) -> None:
    m.phase = "interior/basement"
    # 壁は打ち放しの感じに（間仕切りも）
    for z in range(1, 12):
        for y in range(Y, Y + 3):
            if m.get(3, y, z) == P.WALL_INTERIOR:
                m.set(3, y, z, P.WALL_BASEMENT)
    # 黒い革のソファ（東の壁ぎわ、西を向く）とローテーブル
    for z in range(4, 8):
        m.set(8, Y, z, stairs("polished_blackstone_stairs", "east"))
    m.set(8, Y, 3, B("polished_blackstone_slab", vhalf="bottom"))
    m.set(8, Y, 8, B("polished_blackstone_slab", vhalf="bottom"))
    for z in (5, 6):
        m.set(6, Y, z, B("dark_oak_slab", vhalf="top"))
    for x in (5, 6, 7):
        for z in range(3, 9):
            if m.get(x, Y, z).name == "air":
                m.set(x, Y, z, B("gray_carpet"))
    # 本棚（北の壁）
    for x in range(4, 8):
        m.set(x, Y, 1, B("bookshelf"))
        m.set(x, Y + 1, 1, B("bookshelf"))
    # 東側の棚
    for z in range(9, 12):
        m.set(8, Y, z, B("barrel", facing_direction=1, open_bit=False))
    # 照明（暗め）
    m.set(6, Y + 2, 4, B("lantern", hanging=True))
    m.set(6, Y + 2, 9, B("lantern", hanging=True))
    for x, z in [(4, 3), (7, 10), (4, 7)]:
        light(m, x, Y + 2, z, 9)
    # 物置
    for z in range(7, 12):
        m.set(1, Y, z, B("barrel", facing_direction=1, open_bit=False))
        if z % 2:
            m.set(1, Y + 1, z, B("barrel", facing_direction=1, open_bit=False))
    light(m, 2, Y + 2, 9, 9)
