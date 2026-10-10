"""1階: リビング・台所（食堂）・玄関。作中の「アイスティー」の場面を想定した部屋。確度C。"""
from __future__ import annotations

from ... import palette as P
from ...voxel import AIR, B, Model
from .. import dims as D
from ..parts import leaves, light, stairs

F = D.Y_1F
Y = F + 1  # 立つ高さ


def _floor(m: Model, x0, z0, x1, z1, block):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if m.get(x, F, z).name != "air":
                m.set(x, F, z, block)


def build_living(m: Model) -> None:
    m.phase = "interior/living"
    _floor(m, 1, 5, 6, 11, P.FLOOR_WOOD)
    # テレビ（西の壁ぎわ）
    m.set(1, Y, 9, B("dark_oak_planks"))
    m.set(1, Y, 10, B("dark_oak_planks"))
    m.set(1, Y + 1, 9, P.TV)
    m.set(1, Y + 1, 10, P.TV)
    # ソファ（アイボリー、2人掛け。テレビの方＝西を向く）と肘掛け
    for z in (9, 10):
        m.set(5, Y, z, stairs(P.SOFA_STAIRS, "east"))
    m.set(5, Y, 8, P.SOFA_ARM)
    m.set(5, Y, 11, P.SOFA_ARM)
    # ローテーブルと、盆に載ったグラス2つ（アイスティー）
    m.set(3, Y, 9, P.TABLE_TOP)
    m.set(3, Y, 10, P.TABLE_TOP)
    m.set(3, Y + 1, 9, B("brown_candle", candles=1, lit=False))
    m.set(3, Y + 1, 10, P.TRAY)
    # ラグ
    for x in range(2, 5):
        for z in range(8, 12):
            if m.get(x, Y, z).name == "air":
                m.set(x, Y, z, P.RUG)
    # 一人掛け（北側、南を向く）
    m.set(3, Y, 7, stairs(P.SOFA_STAIRS, "north"))
    # サイドボードと観葉植物
    m.set(1, Y, 11, B("spruce_planks"))
    m.set(1, Y + 1, 11, B("flower_pot", update_bit=False))
    m.set(1, Y, 6, B("decorated_pot", direction=0))
    m.set(1, Y + 1, 6, leaves("azalea"))
    m.set(6, Y, 11, B("decorated_pot", direction=0))
    m.set(6, Y + 1, 11, leaves("azalea"))
    # 照明: ローテーブルの上のペンダントと、見えない光源
    m.set(3, Y + 2, 9, B("lantern", hanging=True))
    for x, z in [(2, 7), (5, 7), (2, 11), (6, 9)]:
        light(m, x, Y + 2, z, 12)


def build_kitchen(m: Model) -> None:
    m.phase = "interior/kitchen"
    _floor(m, 4, 1, 8, 4, P.FLOOR_WOOD_LIGHT)
    _floor(m, 1, 5, 8, 5, P.FLOOR_WOOD_LIGHT)
    # 北の壁ぎわの流し台・コンロ・吊り戸棚
    for x in range(4, 8):
        m.set(x, Y, 1, P.COUNTER)
        m.set(x, Y + 2, 1, P.CABINET)
    m.set(5, Y, 1, B("cauldron", cauldron_liquid="water", fill_level=4))
    m.set(7, Y, 1, B("smoker", cardinal="south"))
    m.set(4, Y + 1, 1, P.GLASS_TEA)  # 作ったアイスティー
    # 冷蔵庫
    m.set(8, Y, 1, B("iron_block"))
    m.set(8, Y + 1, 1, B("iron_block"))
    # 食卓と椅子
    m.set(5, Y, 3, P.TABLE_TOP)
    m.set(6, Y, 3, P.TABLE_TOP)
    for x in (5, 6):
        m.set(x, Y, 2, stairs("oak_stairs", "north"))
        m.set(x, Y, 4, stairs("oak_stairs", "south"))
    m.set(5, Y + 2, 3, B("lantern", hanging=True))
    for x, z in [(4, 3), (8, 3), (7, 5), (2, 5)]:
        light(m, x, Y + 2, z, 12)


def build_genkan(m: Model) -> None:
    m.phase = "interior/genkan"
    # 土間は半ブロック下げる（立つ高さ 4.5。上がりかまちで 5 に上がる）
    for x in (7, 8):
        for z in (7, 8):
            m.set(x, F, z, P.FLOOR_GENKAN)
    # 靴箱（北の壁の下半分）
    m.set(7, Y, 6, P.CABINET)
    m.set(8, Y, 6, P.CABINET)
    m.set(8, Y + 1, 6, B("flower_pot", update_bit=False))
    light(m, 8, Y + 2, 8, 11)
    _ = AIR
