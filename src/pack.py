"""ビヘイビアパック（.mcpack）を組み立てる。"""
from __future__ import annotations

import json
import os
import uuid
import zipfile

from . import params
from .emit_mcfunction import Emission

# UUID はビルドのたびに変えない（ワールドに入れ直したときに別のパック扱いにならないように）
NS = uuid.UUID("6f1d3a52-8c1e-4b8e-9a51-1145141919a0")


def _uuid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


def manifest(target: str, era: str) -> dict:
    label = "最新版 1.26.50 以降" if target == "latest" else "互換版 1.21.130〜1.26.40"
    return {
        "format_version": 2,
        "header": {
            "name": f"野獣邸 再現（{era}・{label}）",
            "description": "個人で遊ぶための建築データ。/function yajuutei/setup → /function yajuutei/build_all",
            "uuid": _uuid(f"header-{target}-{era}"),
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0],
        },
        "modules": [
            {"type": "data", "uuid": _uuid(f"data-{target}-{era}"), "version": [1, 0, 0]},
        ],
    }


def write_pack(em: Emission, era: str, out_dir: str, icon_path: str = None) -> str:
    """out_dir/<pack名>/ にファイルを書き、out_dir/<pack名>.mcpack を作る。パスを返す。"""
    name = f"yajuutei_{era}_{em.target}"
    root = os.path.join(out_dir, name)
    fdir = os.path.join(root, "functions", "yajuutei")
    os.makedirs(fdir, exist_ok=True)
    with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest(em.target, era), f, ensure_ascii=False, indent=2)
    for fname, cmds in em.files.items():
        path = os.path.join(fdir, fname + ".mcfunction")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(cmds) + "\n")
    if icon_path and os.path.exists(icon_path):
        import shutil
        shutil.copy(icon_path, os.path.join(root, "pack_icon.png"))
    mcpack = os.path.join(out_dir, name + ".mcpack")
    with zipfile.ZipFile(mcpack, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(root):
            for fn in sorted(files):
                full = os.path.join(dirpath, fn)
                z.write(full, os.path.relpath(full, root))
    _ = params
    return mcpack
