"""素材 → 統合版ブロックの対応表（MASTER_PROMPT.md §5）。

色調を変えたいときはここだけ書き換えて再ビルドする。
写真との比較で変えたもの（初期案からの変更）は docs/assumptions.md に理由を書いている。
"""
from .voxel import B

# ---- 外装 ----
TILE_WALL = B("light_gray_terracotta")        # 外壁の横長ボーダータイル（グレージュ）
TILE_WALL_ACCENT = B("brown_terracotta")      # 目地の影・腰まわりの濃い段
CONCRETE = B("smooth_stone")                  # 打ち放しコンクリート（写真の明るい灰色に合わせて smooth_stone を主に使う）
CONCRETE_DARK = B("light_gray_concrete")      # 打ち放しの影の面・擁壁
CONCRETE_STAIN = B("tuff")                    # 雨だれ・汚れ（少量）
CONCRETE_SLAB = B("smooth_stone_slab", vhalf="bottom")
CONCRETE_SLAB_TOP = B("smooth_stone_slab", vhalf="top")
LOUVER = B("stripped_mangrove_log", pillar_axis="y")  # 赤茶色の縦ルーバー（縦木目の面で、細かい縦格子を遠目に表現）
LOUVER_OPEN = B("mangrove_fence", noconnect=True)     # 代案: 柵の柱を接続させずに並べる（近くで見ると隙間がある）
WINDOW_FRAME = B("black_concrete")            # 黒いサッシ
GLASS = B("glass_pane")                       # 窓ガラス
GLASS_LACE = B("white_stained_glass_pane")    # レースカーテン越しの窓
GLASS_BLOCK = B("white_stained_glass")        # ガラスブロック
GLASS_BLOCK_ALT = B("glass")
RAIL = B("iron_bars")                         # 縦格子の手すり
RAIL_CAP = B("smooth_stone_slab", vhalf="bottom")
SHUTTER = B("iron_bars")                      # ガレージのグリルシャッター
SHUTTER_BACK = B("gray_concrete")
STAIR_TILE_SLAB = B("mud_brick_slab", vhalf="bottom")      # 外階段（こげ茶のタイル）
STAIR_TILE_SLAB_TOP = B("mud_brick_slab", vhalf="top")
STAIR_TILE_FULL = B("mud_bricks")
OLD_STAIR_SLAB = B("smooth_sandstone_slab", vhalf="bottom")  # 2001年: 門の手前の小口タイルの階段（ベージュ）
OLD_STAIR_SLAB_TOP = B("smooth_sandstone_slab", vhalf="top")
OLD_STAIR_GRAY_SLAB = B("polished_andesite_slab", vhalf="bottom")  # 2001年: 門の奥のグレーの階段
OLD_STAIR_GRAY_SLAB_TOP = B("polished_andesite_slab", vhalf="top")
PORCH_TILE = B("smooth_sandstone")           # 玄関ポーチのベージュのタイル壁
PORCH_FLOOR = B("mud_bricks")
SLATE_STAIRS = "deepslate_tile_stairs"       # 濃いグレーのスレート屋根
SLATE_SLAB = B("deepslate_tile_slab", vhalf="bottom")
SLATE = B("deepslate_tiles")
PENTHOUSE = B("white_concrete")              # 塔屋の白いパネル
PENTHOUSE_TRIM = B("smooth_quartz")
SUNROOM_ROOF = B("light_gray_stained_glass")  # サンルームのガラス（ポリカーボネート）屋根
SUNROOM_POST = B("iron_bars")
DOWNPIPE = B("iron_chain", pillar_axis="y")
ROOF_FLOOR = B("smooth_stone")               # 屋上の床（タイル）
ROOF_FLOOR_ALT = B("light_gray_concrete")
DOOR_ENTRANCE = "iron_door"                  # 玄関扉（グレーの金属）
DOOR_GATE = "dark_oak_door"                  # 門扉（こげ茶）
DOOR_INTERIOR = "birch_door"                 # 室内ドア
DOOR_STEEL = "iron_door"

# ---- 敷地・周辺 ----
ROAD = B("gray_concrete")
ROAD_LINE = B("white_carpet")
GREEN_BELT = B("cyan_carpet")                # 通学路のグリーンベルト（写真①②）
APRON = B("smooth_stone")
SOIL = B("dirt")
GRASS = B("grass_block")
RETAIN_OLD = [B("mossy_cobblestone"), B("cobblestone"), B("tuff"), B("mossy_stone_bricks")]  # 古い石積みの擁壁
BLOCK_WALL = B("stone_bricks")               # コンクリートブロック塀
NEIGHBOR_WALL = B("smooth_quartz")           # 西隣の白いタイルの建物（雰囲気だけ）
NEIGHBOR_OLD_WALL = B("white_concrete_powder")
NEIGHBOR_ROOF = "deepslate_tile_stairs"

# ---- 内装（確度C。静止画が手に入ったら差し替える） ----
FLOOR_WOOD = B("oak_planks")
FLOOR_WOOD_LIGHT = B("birch_planks")
FLOOR_TILE = B("smooth_stone")
FLOOR_GENKAN = B("polished_andesite_slab", vhalf="bottom")
FLOOR_TATAMI = B("bamboo_mosaic")
FLOOR_BASEMENT = B("gray_concrete")
WALL_INTERIOR = B("white_concrete")
WALL_BATH = B("white_concrete")
WALL_BATH_ACCENT = B("light_gray_concrete")
WALL_BASEMENT = B("smooth_stone")
CEILING = B("white_concrete")
SOFA_STAIRS = "smooth_quartz_stairs"         # アイボリーのソファ
SOFA_ARM = B("smooth_quartz_slab", vhalf="bottom")
TABLE_TOP = B("dark_oak_slab", vhalf="top")
COUNTER = B("smooth_quartz")
COUNTER_TOP = B("polished_andesite_slab", vhalf="top")
CABINET = B("spruce_planks")
GLASS_TEA = B("brown_candle", candles=0, lit=False)  # グラスのアイスティー（茶色のろうそくで表現）
TRAY = B("light_weighted_pressure_plate")
RUG = B("light_gray_carpet")
TV = B("black_concrete")
CEILING_LIGHT = B("sea_lantern")
LIGHT = B("light_block_12")                  # 見えない光源
LIGHT_DIM = B("light_block_9")
