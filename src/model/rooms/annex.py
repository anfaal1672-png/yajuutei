"""増築棟（ERA=hybrid/current のときだけ）: ガレージ・応接室・洋室・屋上テラス。確度C。"""
from __future__ import annotations

from ... import palette as P
from ...voxel import B, Model
from .. import dims as D
from ..parts import leaves, light, stairs


def _floor(m: Model, f, x0, z0, x1, z1, block):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if m.get(x, f, z).name != "air":
                m.set(x, f, z, block)


def build_garage(m: Model) -> None:
    """ガレージ。写真①のシャッター越しにバイクが見えるので、黒いバイクを置く。"""
    m.phase = "interior/garage"
    y = D.Y_G + 1
    _floor(m, D.Y_G, 1, 13, 6, 18, P.CONCRETE)
    # バイク（車輪＝砥石、車体＝金床）
    m.set(3, y, 15, B("grindstone", attachment="standing", direction=0))
    m.set(3, y, 16, B("anvil", cardinal="north"))
    m.set(3, y, 17, B("grindstone", attachment="standing", direction=0))
    # 棚
    for z in range(13, 18):
        m.set(6, y, z, B("barrel", facing_direction=1, open_bit=False))
        if z % 2:
            m.set(6, y + 1, z, B("barrel", facing_direction=1, open_bit=False))
    m.set(4, y + 2, 15, B("lantern", hanging=True))
    light(m, 2, y + 2, 13, 11)
    light(m, 5, y + 2, 17, 11)


def build_office(m: Model) -> None:
    """1階の応接室（主屋のリビングとつながる）。"""
    m.phase = "interior/annex_office"
    f = D.Y_1F
    y = f + 1
    _floor(m, f, 1, 13, 6, 18, P.FLOOR_WOOD)
    # 応接セット（黒い革のソファが向かい合う）
    for z in (15, 16):
        m.set(1, y, z, stairs("polished_blackstone_stairs", "west"))
        m.set(5, y, z, stairs("polished_blackstone_stairs", "east"))
        m.set(3, y, z, B("polished_andesite_slab", vhalf="top"))
    for x in (2, 3, 4):
        for z in range(14, 18):
            if m.get(x, y, z).name == "air":
                m.set(x, y, z, B("light_gray_carpet"))
    # 机（正面の窓ぎわ）
    m.set(5, y, 18, B("dark_oak_slab", vhalf="top"))
    m.set(6, y, 18, B("dark_oak_slab", vhalf="top"))
    m.set(6, y + 1, 18, B("lantern", hanging=False))
    m.set(1, y, 13, B("decorated_pot", direction=0))
    m.set(1, y + 1, 13, leaves("azalea"))
    for x, z in [(2, 14), (5, 14), (3, 17)]:
        light(m, x, y + 2, z, 12)


def build_room(m: Model) -> None:
    """2階の洋室（曲面バルコニーに面した部屋）。"""
    m.phase = "interior/annex_room"
    f = D.Y_2F
    y = f + 1
    _floor(m, f, 1, 13, 6, 18, P.FLOOR_WOOD)
    # 窓ぎわの机と椅子
    m.set(2, y, 16, B("dark_oak_slab", vhalf="top"))
    m.set(2, y, 17, B("dark_oak_slab", vhalf="top"))
    m.set(3, y, 16, stairs("spruce_stairs", "east"))
    # 本棚（北の壁ぎわ）
    for x in range(4, 7):
        m.set(x, y, 13, B("bookshelf"))
        m.set(x, y + 1, 13, B("bookshelf"))
    # ソファ
    m.set(6, y, 15, stairs("smooth_quartz_stairs", "east"))
    m.set(6, y, 16, stairs("smooth_quartz_stairs", "east"))
    for x, z in [(3, 14), (5, 14), (4, 17), (2, 13)]:
        light(m, x, y + 2, z, 12)


def build_terrace(m: Model) -> None:
    """増築棟の屋上テラス（3階の和室の前）。"""
    m.phase = "interior/annex_terrace"
    y = D.Y_ANNEX_ROOF + 1
    for x, z in [(2, 13), (6, 17), (6, 13)]:
        m.set(x, y, z, B("decorated_pot", direction=0))
        m.set(x, y + 1, z, leaves("azalea"))
    m.set(3, y, 16, stairs("spruce_stairs", "north"))
    m.set(4, y, 16, stairs("spruce_stairs", "north"))
    light(m, 4, y + 1, 14, 9)
