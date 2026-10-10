"""ビルド: モデル → .mcfunction → .mcpack、平面図と確認用の画像。

  python3 build.py            # パック（hybrid の最新版・互換版、2001 の最新版・互換版）と図
  python3 build.py --no-images
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src import params  # noqa: E402
from src.emit_mcfunction import emit  # noqa: E402
from src.model import build_model  # noqa: E402
from src.model import dims as D  # noqa: E402
from src.pack import write_pack  # noqa: E402
from src.render_preview import Camera, plan_char, render_perspective, render_plan_png  # noqa: E402

CAMERAS = {
    # 写真①〜③と同じ位置・向き（docs/evidence.md の撮影位置の推定）
    "photo1_front_corner": Camera((12.0, 2.6, 27.5), (4, 9.5, 17), fov_v=64, size=(720, 960)),
    "photo2_east_corner": Camera((30.5, 2.6, 28.5), (6, 9, 8), fov_v=48, size=(960, 720)),
    "photo3_entrance_stairs": Camera((9.0, 2.6, 28.5), (9, 8, 10), fov_v=55, size=(720, 960)),
    "overview_southeast": Camera((34, 30, 40), (5, 6, 8), fov_v=45, size=(1200, 900)),
    "overview_southwest": Camera((-22, 26, 36), (5, 6, 8), fov_v=45, size=(1200, 900)),
}

LEVEL_NAMES = [("G", D.Y_G), ("1F", D.Y_1F), ("2F", D.Y_2F), ("3F", D.Y_3F), ("RF", D.Y_ROOF)]


def write_plans(m, era: str, out: str) -> None:
    os.makedirs(out, exist_ok=True)
    x0, x1, z0, z1 = -3, 12, -4, 21
    for name, f in LEVEL_NAMES:
        rows = []
        header = "    " + "".join(str(abs(x) % 10) for x in range(x0, x1 + 1))
        rows.append(header)
        for z in range(z0, z1 + 1):
            rows.append(f"{z:>3} " + "".join(plan_char(m, x, f, z) for x in range(x0, x1 + 1)))
        legend = "記号: # 壁  = 窓  D 扉  ^ 階段  | 手すり・柵  o 家具など  . 床  (空白) 何もない"
        txt = f"{era} {name}（床ブロック y={f}、立つ高さ {f + 1}）\n列=x（{x0}..{x1}）、行=z（{z0}..{z1}、下が道路側）\n{legend}\n\n" + "\n".join(rows) + "\n"
        with open(os.path.join(out, f"{era}_{name}.txt"), "w", encoding="utf-8") as fh:
            fh.write(txt)
        render_plan_png(m, f, x0, z0, x1, z1, os.path.join(out, f"{era}_{name}.png"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "build"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    icon = os.path.join(args.out, "pack_icon.png")
    results = []
    for era in (params.ERA, "2001") if params.ERA != "2001" else ("2001",):
        m = build_model(era)
        if not args.no_images:
            prev = os.path.join(ROOT, "docs", "previews")
            os.makedirs(prev, exist_ok=True)
            for cname, cam in CAMERAS.items():
                render_perspective(m, cam, os.path.join(prev, f"{era}_{cname}.png"))
            write_plans(m, era, os.path.join(ROOT, "docs", "plans"))
            if era == params.ERA:
                ic = Camera((30, 26, 36), (5, 8, 8), fov_v=40, size=(256, 256))
                render_perspective(m, ic, icon)
        for target in ("latest", "compat"):
            em = emit(m, target, era)
            if em.errors:
                print("ERRORS:", em.errors[:10])
                sys.exit(1)
            path = write_pack(em, era, args.out, icon)
            results.append((path, em.stats))
    for path, st in results:
        print(os.path.relpath(path, ROOT), st)


if __name__ == "__main__":
    main()
