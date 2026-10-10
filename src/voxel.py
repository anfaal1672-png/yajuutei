"""ボクセルモデル: (x, y, z) → ブロック。工程（phase）つきで記録する。

座標系（ローカル）:
  x: 西→東（正面道路から建物を見て 左→右）
  y: 下→上（y=0 が道路面のブロック）
  z: 北→南（建物の奥→正面道路）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, Optional, Tuple

Pos = Tuple[int, int, int]

# 作る順番（MASTER_PROMPT.md §6.2）。あとの工程が前の工程を上書きできる。
PHASES = [
    "site",       # 地形・道路・擁壁
    "structure",  # 床・壁・柱・屋根
    "openings",   # 窓・扉
    "exterior",   # 外装の細部（ルーバー、手すり、庇、階段など）
    "interior",   # 内装（間仕切り・床材・家具）
    "props",      # 小物
    "lights",     # 照明
    "planting",   # 植栽
]


@dataclass(frozen=True)
class Block:
    name: str
    states: Tuple[Tuple[str, object], ...] = ()
    # 計算で決める接続（ガラス板・鉄格子・柵）を使わない（すべて非接続）
    noconnect: bool = False

    def with_states(self, **kw) -> "Block":
        d = dict(self.states)
        d.update(kw)
        return Block(self.name, tuple(sorted(d.items())), self.noconnect)

    def state(self, key, default=None):
        for k, v in self.states:
            if k == key:
                return v
        return default


def B(name: str, noconnect: bool = False, **states) -> Block:
    """ブロックを作る。状態名に ':' を含むもの（minecraft:cardinal_direction など）は
    キーワード引数で書けないので、`cardinal=` `vhalf=` の短縮名を使う。"""
    alias = {
        "cardinal": "minecraft:cardinal_direction",
        "vhalf": "minecraft:vertical_half",
        "facing": "minecraft:facing_direction",
    }
    st = {alias.get(k, k): v for k, v in states.items()}
    return Block(name, tuple(sorted(st.items())), noconnect)


AIR = Block("air")


@dataclass
class Model:
    blocks: Dict[Pos, Block] = field(default_factory=dict)
    phase_of: Dict[Pos, str] = field(default_factory=dict)
    # 部屋の名前（通行テスト・平面図用）: (x, y, z) → 部屋名。人が立つ高さ（床の1つ上）に付ける
    rooms: Dict[Pos, str] = field(default_factory=dict)
    phase: str = "site"
    # 工程が初めて現れた順（部屋ごとの工程 "interior/<部屋>" もここに並ぶ）
    phase_order: list = field(default_factory=list)

    # ---- 書き込み ----
    def set(self, x: int, y: int, z: int, block: Block) -> None:
        p = (x, y, z)
        self.blocks[p] = block
        self.phase_of[p] = self.phase
        if not self.phase_order or self.phase_order[-1] != self.phase:
            if self.phase not in self.phase_order:
                self.phase_order.append(self.phase)

    def fill(self, x1, y1, z1, x2, y2, z2, block: Block) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, block)

    def hollow(self, x1, y1, z1, x2, y2, z2, block: Block) -> None:
        """直方体の外周（壁4面）だけ。床・天井は含まない。"""
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.set(x, y, z1, block)
                self.set(x, y, z2, block)
            for z in range(z1, z2 + 1):
                self.set(x1, y, z, block)
                self.set(x2, y, z, block)

    def clear(self, x1, y1, z1, x2, y2, z2) -> None:
        self.fill(x1, y1, z1, x2, y2, z2, AIR)

    def tag_room(self, name: str, x1, z1, x2, z2, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                self.rooms[(x, y, z)] = name

    # ---- 読み出し ----
    def get(self, x: int, y: int, z: int) -> Block:
        return self.blocks.get((x, y, z), AIR)

    def bounds(self) -> Tuple[Pos, Pos]:
        xs = [p[0] for p in self.blocks]
        ys = [p[1] for p in self.blocks]
        zs = [p[2] for p in self.blocks]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def items(self) -> Iterator[Tuple[Pos, Block]]:
        return iter(self.blocks.items())

    def solid_items(self) -> Iterable[Tuple[Pos, Block]]:
        return ((p, b) for p, b in self.blocks.items() if b.name != "air")
