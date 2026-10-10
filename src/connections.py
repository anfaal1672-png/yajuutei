"""ガラス板・鉄格子・柵の接続を計算する（統合版 1.26.50 で状態として指定が必要になったもの）。"""
from __future__ import annotations

from typing import Dict

from .shapes import is_full_cube, kind
from .voxel import Block, Model, Pos

DIRS = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}


def _group(b: Block) -> str:
    k = kind(b)
    if k == "pane":
        return "pane"
    if k == "fence" and b.name.endswith("_fence"):
        return "fence"
    return ""


def connections(m: Model, p: Pos, b: Block) -> Dict[str, bool]:
    g = _group(b)
    out = {}
    for d, (dx, dz) in DIRS.items():
        if b.noconnect:
            out[d] = False
            continue
        nb = m.get(p[0] + dx, p[1], p[2] + dz)
        ng = _group(nb)
        ok = is_full_cube(nb) or (ng == g and ng != "")
        if g == "fence" and nb.noconnect:
            ok = False
        out[d] = ok
    return out


def is_connectable(b: Block) -> bool:
    return _group(b) != ""
