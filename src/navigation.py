"""通行テスト用: プレイヤー（高さ 1.8、ジャンプ 1.25）が歩ける面をたどる幅優先探索。

扉は開けられるものとして通れる（鉄の扉にはボタンを付けている）。
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from .shapes import collision_boxes
from .voxel import Model

HEIGHT = 1.8
JUMP = 1.25
MAX_DROP = 3.0
Node = Tuple[int, int, float]  # x, z, 立つ高さ


class Walker:
    def __init__(self, m: Model):
        self.m = m
        (self.x0, self.y0, self.z0), (self.x1, self.y1, self.z1) = m.bounds()
        self._intervals: Dict[Tuple[int, int], List[Tuple[float, float]]] = {}

    def intervals(self, x: int, z: int) -> List[Tuple[float, float]]:
        key = (x, z)
        if key not in self._intervals:
            iv = []
            for y in range(self.y0, self.y1 + 1):
                b = self.m.blocks.get((x, y, z))
                if b is None:
                    continue
                for bx in collision_boxes(b):
                    iv.append((y + bx[1], y + bx[4]))
            self._intervals[key] = sorted(iv)
        return self._intervals[key]

    def free(self, x: int, z: int, lo: float, hi: float) -> bool:
        for a, b in self.intervals(x, z):
            if a < hi - 1e-6 and b > lo + 1e-6:
                return False
        return True

    def surfaces(self, x: int, z: int) -> List[float]:
        out = []
        for a, b in self.intervals(x, z):
            if self.free(x, z, b, b + HEIGHT):
                out.append(round(b, 4))
        return sorted(set(out))

    def highest_below(self, x: int, z: int, t: float) -> float:
        best = -99.0
        for a, b in self.intervals(x, z):
            if b <= t + 1e-6:
                best = max(best, b)
        return best

    def neighbors(self, n: Node):
        x, z, t = n
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            for t2 in self.surfaces(nx, nz):
                if t2 - t > JUMP or t - t2 > MAX_DROP:
                    continue
                # 上る・下りるときの頭上（高い方の高さで両方の列が空いていること）
                hi = max(t, t2)
                if not self.free(x, z, t, hi + HEIGHT) or not self.free(nx, nz, t2, hi + HEIGHT):
                    continue
                yield (nx, nz, t2)

    def reachable(self, start: Node) -> Set[Node]:
        seen = {start}
        q = deque([start])
        while q:
            n = q.popleft()
            for nb in self.neighbors(n):
                if nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        return seen

    def fall_hazards(self, nodes: Set[Node], min_height: float) -> List[Tuple[Node, Tuple[int, int]]]:
        """そこから一歩踏み出すと 3ブロックより深く落ちる所（手すりの切れ目）。"""
        out = []
        for x, z, t in nodes:
            if t < min_height:
                continue
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if not self.free(nx, nz, t, t + HEIGHT):
                    continue
                if t - self.highest_below(nx, nz, t) > MAX_DROP:
                    out.append(((x, z, t), (nx, nz)))
        return out
