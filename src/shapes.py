"""ブロックの形の分類（接続計算・通行テスト・プレビュー描画で共有する）。"""
from __future__ import annotations

from typing import List, Tuple

from .voxel import Block

Box = Tuple[float, float, float, float, float, float]  # x0,y0,z0,x1,y1,z1（ブロック内 0..1）

PANE_LIKE = ("glass_pane", "iron_bars")  # 名前の末尾で判定
NO_COLLISION_EXACT = {
    "air", "short_grass", "tall_grass", "fern", "large_fern", "vine", "poppy", "dandelion",
    "azure_bluet", "oxeye_daisy", "cornflower", "rose_bush", "lilac", "peony", "bush",
    "wildflowers", "leaf_litter", "short_dry_grass", "tripwire_hook", "lever", "water",
    "lantern", "end_rod", "iron_chain", "frame", "glow_frame", "firefly_bush",
}


def kind(b: Block) -> str:
    n = b.name
    if n.startswith("light_block"):
        return "none"
    if n in NO_COLLISION_EXACT or n.endswith("_button") or n.endswith("candle"):
        return "none"
    if n.endswith("_carpet") or n.endswith("pressure_plate"):
        return "carpet"
    if n.endswith("_door") or n == "wooden_door":
        return "door"
    if n.endswith("_trapdoor"):
        return "trapdoor"
    if n.endswith("_slab"):
        return "slab"
    if n.endswith("_stairs"):
        return "stairs"
    if n.endswith("_fence") or n.endswith("_wall"):
        return "fence"
    if n.endswith(PANE_LIKE):
        return "pane"
    if n in ("bamboo",):
        return "post"
    return "full"


def is_full_cube(b: Block) -> bool:
    return kind(b) == "full" and b.name not in ("cauldron", "flower_pot", "decorated_pot", "lightning_rod", "brewing_stand") \
        and not b.name.endswith("_leaves")


def is_opaque_cube(b: Block) -> bool:
    """描画で隣の面を隠すか（ガラス・葉は隠さない）。"""
    return is_full_cube(b) and "glass" not in b.name


def collision_boxes(b: Block) -> List[Box]:
    k = kind(b)
    if k in ("none", "door"):
        return []
    if k == "carpet":
        return [(0, 0, 0, 1, 1 / 16, 1)]
    if k == "slab":
        if b.state("minecraft:vertical_half") == "top":
            return [(0, 0.5, 0, 1, 1, 1)]
        return [(0, 0, 0, 1, 0.5, 1)]
    if k == "trapdoor":
        if b.state("open_bit"):
            return []
        if b.state("upside_down_bit"):
            return [(0, 13 / 16, 0, 1, 1, 1)]
        return [(0, 0, 0, 1, 3 / 16, 1)]
    if k in ("fence", "pane", "post"):
        return [(0.375, 0, 0.375, 0.625, 1.5, 0.625)]
    if b.name == "cauldron":
        return [(0, 0, 0, 1, 1, 1)]
    if b.name in ("flower_pot", "decorated_pot"):
        return [(0.3, 0, 0.3, 0.7, 0.4, 0.7)]
    # stairs は通行テストでは「1段上がれる箱」として扱う
    return [(0, 0, 0, 1, 1, 1)]
