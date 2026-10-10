"""部屋ごとの内装。1部屋1関数で、あとから部屋単位で作り直せるようにしている。

すべて確度C（作中の静止画がない状態で、2000年前後の都内の RC 住宅として推測）。
静止画が手に入ったら、該当する関数だけを書き換える（docs/assumptions.md A-20 以降）。
"""
from __future__ import annotations

from typing import Callable, Dict

from ...voxel import Model
from . import annex, basement, first, second, third

# 部屋名 → 内装を作る関数。emit で部屋ごとの .mcfunction に分ける
ROOM_BUILDERS: Dict[str, Callable[[Model], None]] = {
    "basement": basement.build,
    "living": first.build_living,
    "kitchen": first.build_kitchen,
    "genkan": first.build_genkan,
    "bath": second.build_bath,
    "toilet": second.build_toilet,
    "bedroom": second.build_bedroom,
    "study": second.build_study,
    "washitsu": third.build_washitsu,
    "storage": third.build_storage,
}
ANNEX_BUILDERS: Dict[str, Callable[[Model], None]] = {
    "garage": annex.build_garage,
    "annex_office": annex.build_office,
    "annex_room": annex.build_room,
    "annex_terrace": annex.build_terrace,
}
