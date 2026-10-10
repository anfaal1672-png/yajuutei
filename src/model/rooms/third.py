"""3階: 和室・納戸。確度C。"""
from __future__ import annotations

from ... import palette as P
from ...voxel import B, Model
from .. import dims as D
from ..parts import leaves, light

F = D.Y_3F
Y = F + 1


def _floor(m: Model, x0, z0, x1, z1, block):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if m.get(x, F, z).name != "air":
                m.set(x, F, z, block)


def build_washitsu(m: Model) -> None:
    m.phase = "interior/washitsu"
    _floor(m, 1, 6, 8, 9, P.FLOOR_TATAMI)
    _floor(m, 1, 5, 2, 5, P.FLOOR_WOOD)
    # 座卓と座布団
    for x in (4, 5):
        for z in (7, 8):
            m.set(x, Y, z, B("spruce_slab", vhalf="bottom"))
    for x, z in [(3, 7), (6, 8), (4, 9)]:
        m.set(x, Y, z, B("red_carpet"))
    # 床の間（東の奥）: 一段上げた床板と花
    m.set(8, Y, 6, B("spruce_slab", vhalf="bottom"))
    m.set(8, Y, 7, B("spruce_slab", vhalf="bottom"))
    m.set(8, Y + 1, 6, B("decorated_pot", direction=0))
    m.set(8, Y + 2, 6, leaves("cherry"))
    # 押入れ（西の壁ぎわ）
    m.set(1, Y, 9, B("birch_planks"))
    m.set(1, Y + 1, 9, B("birch_planks"))
    # 和風の吊り灯り
    m.set(4, Y + 2, 7, B("lantern", hanging=True))
    for x, z in [(2, 7), (7, 8), (6, 6)]:
        light(m, x, Y + 2, z, 12)


def build_storage(m: Model) -> None:
    m.phase = "interior/storage"
    _floor(m, 4, 1, 8, 4, P.FLOOR_WOOD)
    for x in range(4, 9):
        m.set(x, Y, 1, B("barrel", facing_direction=1, open_bit=False))
        if x % 2:
            m.set(x, Y + 1, 1, B("barrel", facing_direction=1, open_bit=False))
    for z in (2, 3):
        m.set(8, Y, z, B("barrel", facing_direction=1, open_bit=False))
    light(m, 6, Y + 2, 3, 11)
