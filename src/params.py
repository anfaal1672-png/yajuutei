"""再現のパラメータ（MASTER_PROMPT.md §4）。ここを書き換えて `make` すれば反映される。

採用した値の理由は docs/params.md を参照。
"""

# いつの姿か: "hybrid"（外観は2020年代の写真、内装は作中準拠）/ "2001" / "current"
#   2001   : 前面の増築棟（ガレージ・曲面バルコニー）を作らず、前面は駐車スペース＋門付き階段にする（写真③の状態）
#   current: hybrid と同じ外観。内装は区別できる資料がないため hybrid と同じになる
ERA = "hybrid"

# 縮尺。実物の 1m を何ブロックにするか（水平）。
# 階高は 4ブロック（天井高3＋床1）で固定。実物の階高は約3mなので、
# 外形の縦横比を保つため水平も 1.25 にしている（docs/assumptions.md A-01）。
SCALE = 1.25
STORY = 4  # 階高（ブロック）

# 敷地の範囲: "building" / "lot" / "block"（周辺の街区の雰囲気まで）
SITE = "block"

# 内装の範囲: "all"（全室。作中の部屋は詳細）/ "scenes"（作中の部屋だけ）
INTERIOR = "all"

# 対象バージョン（Mojang/bedrock-samples の最新安定版タグ 2026-09-15 で確認）
VERSION = "1.26.50"
# 互換版パックの下限（1.21.130 のブロック定義で確認）
COMPAT_VERSION = "1.21.130"

# 実行位置: プレイヤーが立つ場所（ローカル座標）。前面道路の中央、建物の正面。
# ここで /function を実行すると、ローカル座標 (x, y, z) が
# ワールドの (~x-ORIGIN_X, ~y-ORIGIN_Y, ~z-ORIGIN_Z) になる。
ORIGIN_X = 5
ORIGIN_Y = 1   # 足の高さ。ローカル y=0 が足元の地面ブロックになる
ORIGIN_Z = 24
