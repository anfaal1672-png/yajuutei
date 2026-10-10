"""モデル → .mcfunction（統合版のビヘイビアパックの関数）。

- 座標はすべて実行位置からの相対（~）。実行位置 = params.ORIGIN（前面道路の中央）。
- まず範囲全体を空気で消してから、工程の順に置く。最終的に空気になる所は何も出さない。
- 同じブロックが直方体に並ぶ所は /fill にまとめる（1回 32,768 ブロックまで）。
- 支えが必要なブロック（扉・照明・植物・水など）は、各工程の最後に下から順に置く。
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from . import params
from .blocks_bedrock import format_block, states_for_target, validate
from .connections import connections, is_connectable
from .model import dims as D
from .shapes import kind
from .voxel import PHASES, Block, Model

FILL_LIMIT = 32768
FUNCTION_LIMIT = 10000  # ゲームルール functionCommandLimit の既定値

ATTACHED_PREFIX = ("lantern", "vine", "bamboo", "short_grass", "fern", "azalea", "flowering_azalea",
                   "lever", "tripwire_hook", "water", "lightning_rod")


def is_attached(b: Block) -> bool:
    k = kind(b)
    if k in ("door", "carpet"):
        return True
    n = b.name
    return n in ATTACHED_PREFIX or n.endswith("_button") or n.endswith("candle")


def rel(x: int, y: int, z: int) -> str:
    def r(v):
        return "~" if v == 0 else f"~{v}"
    return f"{r(x - params.ORIGIN_X)} {r(y - params.ORIGIN_Y)} {r(z - params.ORIGIN_Z)}"


@dataclass
class Emission:
    target: str
    files: Dict[str, List[str]] = field(default_factory=dict)   # 関数名 → コマンド
    order: List[str] = field(default_factory=list)              # build_all で呼ぶ順
    errors: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)


def _phase_key(phase: str, model: Model) -> Tuple[int, int]:
    base = phase.split("/")[0]
    return (PHASES.index(base), model.phase_order.index(phase))


def final_block_string(m: Model, p, b: Block, target: str, errors: List[str]) -> str:
    extra = {}
    if target == "latest" and is_connectable(b):
        c = connections(m, p, b)
        extra = {f"minecraft:connection_{d}": v for d, v in c.items()}
    st = states_for_target(b, extra, target)
    ok, msg = validate(b, st, target)
    if not ok:
        errors.append(f"{p}: {msg}")
    return format_block(b.name, st)


def greedy_boxes(cells: set) -> List[Tuple[int, int, int, int, int, int]]:
    """同じブロックの集合を直方体に分ける（y→z→x の順で走査して x, z, y 方向へ伸ばす）。"""
    remaining = set(cells)
    boxes = []
    for p in sorted(cells, key=lambda q: (q[1], q[2], q[0])):
        if p not in remaining:
            continue
        x0, y0, z0 = p
        x1 = x0
        while (x1 + 1, y0, z0) in remaining:
            x1 += 1
        z1 = z0
        while all((x, y0, z1 + 1) in remaining for x in range(x0, x1 + 1)):
            z1 += 1
        y1 = y0
        while all((x, y1 + 1, z) in remaining for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)):
            if (x1 - x0 + 1) * (z1 - z0 + 1) * (y1 - y0 + 2) > FILL_LIMIT:
                break
            y1 += 1
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    remaining.discard((x, y, z))
        boxes.append((x0, y0, z0, x1, y1, z1))
    return boxes


def _commands_for(blocks: Dict[Tuple[int, int, int], str], attached_flags: Dict[str, bool]) -> List[str]:
    by_block: Dict[str, set] = defaultdict(set)
    for p, s in blocks.items():
        by_block[s].add(p)
    solid, att = [], []
    for s, cells in by_block.items():
        for bx in greedy_boxes(cells):
            x0, y0, z0, x1, y1, z1 = bx
            if bx[:3] == bx[3:]:
                cmd = f"setblock {rel(x0, y0, z0)} {s}"
            else:
                cmd = f"fill {rel(x0, y0, z0)} {rel(x1, y1, z1)} {s}"
            (att if attached_flags[s] else solid).append((y0, cmd))
    solid.sort(key=lambda t: t[0])
    att.sort(key=lambda t: t[0])
    return [c for _, c in solid] + [c for _, c in att]


def clear_commands(fill_ground: bool) -> List[str]:
    (bx0, by0, bz0), (bx1, by1, bz1) = D.BBOX
    cmds = []
    dx = bx1 - bx0 + 1
    dy = by1 - 1 + 1
    step = max(1, FILL_LIMIT // (dx * dy))
    z = bz0
    while z <= bz1:
        z2 = min(bz1, z + step - 1)
        cmds.append(f"fill {rel(bx0, 1, z)} {rel(bx1, by1, z2)} air")
        z = z2 + 1
    if fill_ground:
        cmds.append(f"fill {rel(bx0, 0, bz0)} {rel(bx1, 0, bz1)} grass_block")
    return cmds


def emit(m: Model, target: str, era: str) -> Emission:
    em = Emission(target=target)
    groups: Dict[str, Dict] = defaultdict(dict)
    flags: Dict[str, bool] = {}
    for p, b in m.items():
        if b.name == "air":
            continue
        s = final_block_string(m, p, b, target, em.errors)
        flags[s] = is_attached(b)
        groups[m.phase_of[p]][p] = s

    def say(text: str) -> str:
        return 'tellraw @a {"rawtext":[{"text":"' + text + '"}]}'

    em.files["clear"] = clear_commands(True) + [say("§e[野獣邸] 範囲を消しました")]
    em.files["build/00_clear"] = clear_commands(False)
    em.order.append("build/00_clear")
    phases = sorted(groups.keys(), key=lambda ph: _phase_key(ph, m))
    for i, ph in enumerate(phases, start=1):
        name = f"build/{i:02d}_{ph.replace('/', '_')}"
        em.files[name] = _commands_for(groups[ph], flags)
        em.order.append(name)
    total = sum(len(em.files[n]) for n in em.order)
    em.files["build_all"] = (
        [say(f"§e[野獣邸] 建築を始めます（{era} / {target}）")]
        + [f"function yajuutei/{n}" for n in em.order]
        + [say("§a[野獣邸] 完成しました")]
    )
    (bx0, by0, bz0), (bx1, by1, bz1) = D.BBOX
    em.files["setup"] = [
        f"tickingarea add {rel(bx0, 0, bz0)} {rel(bx1, by1, bz1)} yajuutei true",
        say("§e[野獣邸] この場所を読み込み範囲（tickingarea）に登録しました。続けて /function yajuutei/build_all"),
    ]
    em.files["remove_tickingarea"] = ["tickingarea remove yajuutei"]
    # 部屋だけ作り直す関数（静止画で内装を差し替えたあとに使う）
    for ph in phases:
        if ph.startswith("interior/"):
            em.files[f"rooms/{ph.split('/', 1)[1]}"] = list(em.files[f"build/{phases.index(ph) + 1:02d}_{ph.replace('/', '_')}"])
    em.stats = {
        "total_build_commands": total + len(em.files["build_all"]),
        "blocks": sum(len(g) for g in groups.values()),
        "functions": len(em.files),
        "max_function_commands": max(len(v) for v in em.files.values()),
    }
    return em
