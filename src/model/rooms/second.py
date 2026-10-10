"""2階: 浴室・トイレ・寝室・書斎。確度C。"""
from __future__ import annotations

from ... import palette as P
from ...voxel import B, Model
from .. import dims as D
from ..parts import light, stairs

F = D.Y_2F
Y = F + 1


def _floor(m: Model, x0, z0, x1, z1, block):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if m.get(x, F, z).name != "air":
                m.set(x, F, z, block)


def build_bath(m: Model) -> None:
    """浴室（作中でシャワーを浴びる場面を想定）。東の壁はガラスブロック。"""
    m.phase = "interior/bath"
    _floor(m, 7, 1, 8, 4, P.FLOOR_TILE)
    # 浴槽（2×2。縁は白いブロック／洗面台、中に水）。水が漏れないよう周りはすべて流れを止めるブロック
    for x in (7, 8):
        for z in (1, 2):
            m.set(x, Y, z, B("water", liquid_depth=0))
    m.set(8, Y, 3, B("smooth_quartz", pillar_axis="y"))
    m.set(7, Y, 3, B("cauldron", cauldron_liquid="water", fill_level=3))  # 洗面台
    m.set(7, Y + 1, 3, B("glass_pane"))  # 鏡
    # 便器（ユニットバス）
    m.set(8, Y, 4, stairs("smooth_quartz_stairs", "east"))
    # シャワー（壁の水栓とシャワーヘッド。浴槽の上）
    m.set(7, Y + 1, 2, B("lever", lever_direction="east", open_bit=False))
    m.set(7, Y + 2, 1, B("lightning_rod", facing_direction=0, powered_bit=False))
    # 腰の高さまで薄いグレーのタイル
    for z in range(1, 5):
        if m.get(6, Y, z) == P.WALL_INTERIOR:
            m.set(6, Y, z, P.WALL_BATH_ACCENT)
    light(m, 8, Y + 2, 2, 12)
    light(m, 7, Y + 2, 4, 11)


def build_toilet(m: Model) -> None:
    m.phase = "interior/toilet"
    # 2階の便器は浴室の中（build_bath）。ここでは廊下の明かりだけ
    light(m, 7, Y + 2, 6, 10)


def build_bedroom(m: Model) -> None:
    m.phase = "interior/bedroom"
    _floor(m, 1, 6, 8, 11, P.FLOOR_WOOD)
    # ベッド（頭板＋白い布団。統合版のベッドは色を指定できないので羊毛で作る）
    for x in (5, 6):
        m.set(x, Y, 8, B("dark_oak_planks"))
        m.set(x, Y + 1, 8, B("dark_oak_slab", vhalf="bottom"))
        m.set(x, Y, 9, B("white_wool"))
        m.set(x, Y, 10, B("white_wool"))
        m.set(x, Y + 1, 9, B("white_carpet"))
        m.set(x, Y + 1, 10, B("light_blue_carpet"))
    # ナイトテーブルとスタンド
    m.set(7, Y, 8, B("spruce_planks"))
    m.set(7, Y + 1, 8, B("lantern", hanging=False))
    # 洋服だんす
    for z in (8, 9):
        m.set(1, Y, z, P.CABINET)
        m.set(1, Y + 1, z, P.CABINET)
    # 鏡台
    m.set(8, Y, 8, B("spruce_planks"))
    m.set(8, Y + 1, 8, B("glass_pane"))
    # ラグ
    for x in range(2, 8):
        for z in (10, 11):
            if m.get(x, Y, z).name == "air":
                m.set(x, Y, z, B("brown_carpet"))
    for x, z in [(2, 10), (7, 10), (5, 11)]:
        light(m, x, Y + 2, z, 12)
    # 廊下
    _floor(m, 1, 5, 8, 6, P.FLOOR_WOOD)
    light(m, 4, Y + 2, 6, 11)


def build_study(m: Model) -> None:
    m.phase = "interior/study"
    _floor(m, 4, 1, 5, 4, P.FLOOR_WOOD)
    m.set(4, Y, 1, B("dark_oak_slab", vhalf="top"))
    m.set(5, Y, 1, B("dark_oak_slab", vhalf="top"))
    m.set(4, Y, 2, stairs("spruce_stairs", "south"))
    m.set(5, Y + 1, 1, B("lantern", hanging=False))
    for z in (3, 4):
        m.set(5, Y, z, B("bookshelf"))
        m.set(5, Y + 1, z, B("bookshelf"))
    light(m, 4, Y + 2, 3, 12)
