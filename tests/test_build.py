"""自動テスト（MASTER_PROMPT.md §6.5）。"""
from __future__ import annotations

import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src import params  # noqa: E402
from src.emit_mcfunction import FILL_LIMIT, FUNCTION_LIMIT, emit, rel  # noqa: E402
from src.model import build_model  # noqa: E402
from src.model import dims as D  # noqa: E402
from src.model.plans import ROOMS  # noqa: E402
from src.navigation import Walker  # noqa: E402
from src.voxel import AIR  # noqa: E402

ERAS = ["hybrid", "2001"]
TARGETS = ["latest", "compat"]


@pytest.fixture(scope="module", params=ERAS)
def model(request):
    return request.param, build_model(request.param)


# ---------------------------------------------------------------- ブロックとコマンド
@pytest.mark.parametrize("target", TARGETS)
def test_all_blocks_and_states_are_verified(model, target):
    era, m = model
    em = emit(m, target, era)
    assert em.errors == []


@pytest.mark.parametrize("target", TARGETS)
def test_fill_volume_and_function_limits(model, target):
    era, m = model
    em = emit(m, target, era)
    pat = re.compile(r"^fill (\S+) (\S+) (\S+) (\S+) (\S+) (\S+) ")
    for name, cmds in em.files.items():
        assert len(cmds) <= FUNCTION_LIMIT, name
        for c in cmds:
            mm = pat.match(c)
            if mm:
                v = [int(t[1:] or 0) for t in mm.groups()]
                vol = (abs(v[3] - v[0]) + 1) * (abs(v[4] - v[1]) + 1) * (abs(v[5] - v[2]) + 1)
                assert vol <= FILL_LIMIT, c
    # build_all から実行されるコマンドの合計（入れ子を含む）も上限以下
    assert em.stats["total_build_commands"] <= FUNCTION_LIMIT


COMMAND_RE = re.compile(
    r"^(fill (~-?\d*\s){6}[a-z0-9_]+( \[[^\]]+\])?"
    r"|setblock (~-?\d*\s){3}[a-z0-9_]+( \[[^\]]+\])?"
    r"|function yajuutei/[a-z0-9_/]+"
    r"|tellraw @a \{.*\}"
    r"|tickingarea (add (~-?\d*\s){6}yajuutei true|remove yajuutei))$"
)


@pytest.mark.parametrize("target", TARGETS)
def test_command_syntax(model, target):
    era, m = model
    em = emit(m, target, era)
    for name, cmds in em.files.items():
        for c in cmds:
            assert COMMAND_RE.match(c), f"{name}: {c}"
            assert "minecraft:connection" not in c or target == "latest"


def test_compat_has_no_new_states(model):
    era, m = model
    em = emit(m, "compat", era)
    text = "\n".join(c for cmds in em.files.values() for c in cmds)
    assert "minecraft:connection_" not in text
    assert "minecraft:corner" not in text


def test_function_references_exist(model):
    era, m = model
    em = emit(m, "latest", era)
    for cmds in em.files.values():
        for c in cmds:
            if c.startswith("function "):
                assert c.split("yajuutei/", 1)[1] in em.files


def test_attached_blocks_have_support(model):
    """扉・照明・ツタ・ボタン・水などは、支えのブロックが同じかそれより前の工程にあること。"""
    era, m = model
    for (x, y, z), b in m.items():
        n = b.name
        if n.endswith("_door") and not b.state("upper_block_bit"):
            assert m.get(x, y - 1, z).name != "air", ("door floor", (x, y, z))
            up = m.get(x, y + 1, z)
            assert up.name == n and up.state("upper_block_bit"), ("door top", (x, y, z))
        if n == "lantern" and b.state("hanging"):
            assert m.get(x, y + 1, z).name != "air", ("lantern", (x, y, z))
        if n in ("bamboo",):
            below = m.get(x, y - 1, z).name
            assert below in ("bamboo", "grass_block", "dirt"), ((x, y, z), below)
        if n == "water":
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = m.get(x + dx, y, z + dz).name
                assert nb != "air", ("water leaks", (x, y, z))
            assert m.get(x, y - 1, z).name != "air"


# ---------------------------------------------------------------- 寸法（docs/evidence.md）
def test_dimensions(model):
    era, m = model
    # 主屋の幅 10・奥行き 13、階高 4
    assert m.get(D.HX0, D.Y_1F + 1, D.HZ0).name != "air"
    assert m.get(D.HX1, D.Y_1F + 1, D.HZ0).name != "air"
    assert D.HX1 - D.HX0 + 1 == 10 and D.HZ1 - D.HZ0 + 1 == 13
    assert D.Y_2F - D.Y_1F == 4 == params.STORY
    # 塔屋の屋根の高さ（道路から 20ブロック = 16m）
    assert m.get(1, D.Y_PH_ROOF, 1).name != "air"
    if era != "2001":
        # 増築棟の正面の幅 8、ガレージのシャッター幅 5
        assert D.AX1 - D.AX0 + 1 == 8
        assert [m.get(x, 2, D.AZ1).name for x in range(1, 6)] == ["iron_bars"] * 5
        # 曲面バルコニーのルーバー
        assert m.get(0, D.Y_2F + 3, 20).name == "stripped_mangrove_log"


# ---------------------------------------------------------------- 通行・安全
@pytest.fixture(scope="module")
def reach(model):
    era, m = model
    w = Walker(m)
    nodes = w.reachable((params.ORIGIN_X, params.ORIGIN_Z, 1.0))
    by = {}
    for x, z, h in nodes:
        by.setdefault((x, z), set()).add(h)
    return era, m, w, nodes, by


def _reached(by, x0, z0, x1, z1, lo, hi):
    return any(lo <= h <= hi for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) for h in by.get((x, z), ()))


def test_every_room_is_reachable_from_the_street(reach):
    era, m, w, nodes, by = reach
    for level, rooms in ROOMS.items():
        f = D.LEVELS[level]
        for name, x0, z0, x1, z1 in rooms:
            if era == "2001" and z0 >= D.AZ0:
                continue
            assert _reached(by, x0, z0, x1, z1, f + 0.4, f + 1.6), (level, name)


def test_roofs_and_terraces_are_reachable(reach):
    era, m, w, nodes, by = reach
    assert _reached(by, 4, 7, 8, 9, D.Y_ROOF + 0.9, D.Y_ROOF + 1.1)          # 屋上
    assert _reached(by, 0, 11, 9, 11, D.Y_3F + 0.9, D.Y_3F + 1.1)           # 3階前のテラス
    assert _reached(by, D.SX0, D.HZ1 + 1, D.SX0, D.HZ1 + 1, D.Y_2F + 0.9, D.Y_2F + 1.1)  # ポーチの上のバルコニー
    if era != "2001":
        assert _reached(by, 1, 13, 6, 18, D.Y_ANNEX_ROOF + 0.9, D.Y_ANNEX_ROOF + 1.1)  # 増築棟の屋上
        assert _reached(by, 1, 19, 5, 19, D.Y_2F + 0.9, D.Y_2F + 1.1)                  # 曲面バルコニー


def test_no_gaps_in_upper_railings(reach):
    era, m, w, nodes, by = reach
    assert w.fall_hazards(nodes, D.Y_2F + 1) == []


def test_fall_hazard_check_detects_a_missing_rail(reach):
    """手すりを1本抜くと検出できること（テスト自体の確認）。"""
    era, m, w, nodes, by = reach
    p = (6, D.Y_ROOF + 1, D.HZ0)
    saved, saved2 = m.get(*p), m.get(p[0], p[1] + 1, p[2])
    try:
        m.set(*p, AIR)
        m.set(p[0], p[1] + 1, p[2], AIR)
        w2 = Walker(m)
        n2 = w2.reachable((params.ORIGIN_X, params.ORIGIN_Z, 1.0))
        assert w2.fall_hazards(n2, D.Y_2F + 1)
    finally:
        m.set(*p, saved)
        m.set(p[0], p[1] + 1, p[2], saved2)


# ---------------------------------------------------------------- 配慮（MASTER_PROMPT.md §2）
FORBIDDEN = ["北沢", "下北", "世田谷", "茶沢", "Kitazawa", "Shimokitazawa", "Setagaya", "Chazawa", "23-14"]


def test_no_address_in_repository():
    skip_dirs = {".git", ".cache", "build", "refs/private", "__pycache__", ".pytest_cache"}
    for dirpath, dirnames, files in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        if any(rel_dir == d or rel_dir.startswith(d + os.sep) for d in skip_dirs):
            dirnames[:] = []
            continue
        for fn in files:
            if fn.endswith((".png", ".jpg", ".mcpack", ".pyc")):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="ignore").read()
            for w in FORBIDDEN:
                if w in text and not path.endswith("test_build.py"):
                    raise AssertionError(f"{w} in {path}")


def test_private_refs_are_ignored():
    gi = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
    assert "refs/private/" in gi


def test_relative_coordinates_origin():
    assert rel(params.ORIGIN_X, params.ORIGIN_Y, params.ORIGIN_Z) == "~ ~ ~"
