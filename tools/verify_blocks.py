"""使っているブロックとブロック状態を、Mojang 公式のブロック定義と突き合わせて
src/blocks_bedrock_data.py を作る（使うブロックの分だけ書き出す）。

出典: https://github.com/Mojang/bedrock-samples の metadata/vanilladata_modules/mojang-blocks.json
  - 最新安定版: タグ v1.26.50.4（2026-09-15）
  - 互換版:     タグ v1.21.130.3（2025-12-09）
ダウンロードしたファイルは .cache/ に置く（リポジトリには入れない）。

使い方: python3 -m tools.verify_blocks
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.model import build_model  # noqa: E402

TAGS = {"latest": "v1.26.50.4", "compat": "v1.21.130.3"}
URL = "https://raw.githubusercontent.com/Mojang/bedrock-samples/{tag}/metadata/vanilladata_modules/mojang-blocks.json"


def load(tag: str) -> dict:
    path = os.path.join(ROOT, ".cache", f"mojang-blocks-{tag.lstrip('v')}.json")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(URL.format(tag=tag), path)
    d = json.load(open(path, encoding="utf-8"))
    props = {p["name"]: [v["value"] for v in p["values"]] for p in d["block_properties"]}
    out = {}
    for it in d["data_items"]:
        out[it["name"].split(":", 1)[1]] = {p["name"]: props[p["name"]] for p in it["properties"]}
    return out


def used_blocks():
    names = set()
    for era in ("hybrid", "2001"):
        m = build_model(era)
        for _, b in m.items():
            names.add(b.name)
    names |= {"air", "grass_block"}
    return sorted(names)


def main():
    data = {k: load(t) for k, t in TAGS.items()}
    used = used_blocks()
    missing = [n for n in used if n not in data["latest"]]
    lines = [
        '"""統合版のブロック定義（使っているブロックの分だけ）。tools/verify_blocks.py が生成する。',
        "",
        f"出典: Mojang/bedrock-samples {TAGS['latest']}（最新安定版）と {TAGS['compat']}（互換版）の",
        "metadata/vanilladata_modules/mojang-blocks.json。手で書き換えない。",
        '"""',
        "",
        f"LATEST_TAG = {TAGS['latest']!r}",
        f"COMPAT_TAG = {TAGS['compat']!r}",
        "",
        "# ブロック名 → {状態名: [取りうる値]}",
        "LATEST = {",
    ]
    for n in used:
        if n in data["latest"]:
            lines.append(f"    {n!r}: {data['latest'][n]!r},")
    lines.append("}")
    lines.append("")
    lines.append("# 互換版（1.21.130）。存在しないブロックは None")
    lines.append("COMPAT = {")
    for n in used:
        lines.append(f"    {n!r}: {data['compat'].get(n)!r},")
    lines.append("}")
    path = os.path.join(ROOT, "src", "blocks_bedrock_data.py")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(used)} blocks written to {path}")
    if missing:
        print("NOT FOUND in latest:", missing)
        sys.exit(1)
    cmissing = [n for n in used if data["compat"].get(n) is None]
    if cmissing:
        print("not in compat:", cmissing)


if __name__ == "__main__":
    main()
