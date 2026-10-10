"""統合版コマンドのブロックの書き方（ブロック名＋ブロック状態）と検証。

ブロック状態の書き方: `["状態名"=値,...]`（文字列は "" で囲む、真偽値は true/false、数値はそのまま）。
出典:
  - ブロック名・状態名・値: Mojang/bedrock-samples の mojang-blocks.json（blocks_bedrock_data.py に抜粋）
  - 書式: Microsoft Learn「Block States」「/setblock」「/fill」コマンドリファレンス
  - 1.26.50 で柵・ガラス板・鉄格子に minecraft:connection_*、階段に minecraft:corner が追加された
    （1.21.130 の定義には無い）。最新版パックでは接続を計算して明示し、互換版パックでは書かない。
"""
from __future__ import annotations

from typing import Dict, Tuple

from .blocks_bedrock_data import COMPAT, LATEST
from .voxel import Block


def _fmt_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return f'"{v}"'


def format_block(name: str, states: Dict[str, object]) -> str:
    if not states:
        return name
    inner = ",".join(f'"{k}"={_fmt_value(v)}' for k, v in sorted(states.items()))
    return f"{name} [{inner}]"


def states_for_target(b: Block, extra: Dict[str, object], target: str) -> Dict[str, object]:
    """対象バージョンで有効な状態だけを残す。"""
    st = dict(b.states)
    st.update(extra)
    table = LATEST if target == "latest" else COMPAT
    allowed = table.get(b.name) or {}
    return {k: v for k, v in st.items() if k in allowed}


def validate(b: Block, states: Dict[str, object], target: str) -> Tuple[bool, str]:
    table = LATEST if target == "latest" else COMPAT
    if b.name not in table or table[b.name] is None:
        return False, f"unknown block {b.name} for {target}"
    allowed = table[b.name]
    for k, v in states.items():
        if k not in allowed:
            return False, f"{b.name}: unknown state {k}"
        if v not in allowed[k]:
            return False, f"{b.name}: bad value {k}={v!r} (allowed {allowed[k]})"
    return True, ""
