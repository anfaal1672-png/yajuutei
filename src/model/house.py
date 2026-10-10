"""主屋と増築棟の構造・開口部・外装（工程 structure / openings / exterior）。"""
from __future__ import annotations

from .. import palette as P
from ..voxel import AIR, B, Model
from . import dims as D
from .parts import door, railing, stairs
from .plans import ANNEX, REAR

WALLISH = set("#wdD")
FLOOR_STRUCT = B("oak_planks")  # 構造の床（内装の工程で部屋ごとの仕上げに置き換える）


def _cells(plan, x0, z0):
    for dz, row in enumerate(plan):
        for dx, c in enumerate(row):
            if c != " ":
                yield x0 + dx, z0 + dz, c


def _plan_char(plan, x0, z0, x, z):
    dz, dx = z - z0, x - x0
    if 0 <= dz < len(plan) and 0 <= dx < len(plan[dz]):
        return plan[dz][dx]
    return " "


def _ext_wall(level: str):
    return P.CONCRETE if level == "G" else P.TILE_WALL


def _build_level(m: Model, plan, x0, z0, level: str, floor_band=None, height: int = 3):
    f = D.LEVELS[level]
    ext = _ext_wall(level)
    for x, z, c in _cells(plan, x0, z0):
        if c == "#":
            m.set(x, f, z, floor_band or ext)
        else:
            m.set(x, f, z, FLOOR_STRUCT if level != "G" else P.FLOOR_BASEMENT)
        for y in range(f + 1, f + 1 + height):
            if c in "#D":
                m.set(x, y, z, ext)
            elif c in "wd":
                m.set(x, y, z, P.WALL_INTERIOR)
            else:
                m.set(x, y, z, AIR)


def door_facing(plan, x0, z0, x, z) -> str:
    l = _plan_char(plan, x0, z0, x - 1, z)
    r = _plan_char(plan, x0, z0, x + 1, z)
    return "south" if (l in WALLISH or r in WALLISH) else "east"


def balcony_outline():
    """2階の曲面バルコニー: 手すり壁（外周）と床。写真①の弧を 1ブロック単位で近似。"""
    parapet = [(-1, z) for z in range(15, 20)] + [(x, 20) for x in range(0, 6)]
    floor = [(0, z) for z in range(16, 20)] + [(x, 19) for x in range(1, 6)]
    return parapet, floor


def annex_roof_cells():
    """増築棟の屋根（立つ高さ y=14）。主屋の南壁の上（z=12）も含む。"""
    cells = {(x, z) for x, z, c in _cells(ANNEX["2F"], D.AX0, D.AZ0)}
    cells |= {(x, D.HZ1) for x in range(D.AX0, D.AX1 + 1)}
    return cells


ANNEX_ROOF_STEP = (1, D.HZ1)  # テラス（立つ高さ13）から増築棟の屋根（14）へ上がる段の位置


def terrace_cells(era: str):
    """3階の前のテラス（2階の屋根、立つ高さ 13）。"""
    cells = {(x, z) for x in range(D.HX0, D.HX1 + 1) for z in range(D.H3_Z1 + 1, D.HZ1 + 1)}
    if era != "2001":
        cells -= annex_roof_cells()
    return cells


def _edge(cells, blocked):
    edge = []
    for x, z in sorted(cells):
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, z + dz)
            if q not in cells and q not in blocked:
                edge.append((x, z))
                break
    return edge


def terrace_edge(era: str):
    building = {(x, z) for x in range(D.HX0, D.HX1 + 1) for z in range(D.HZ0, D.H3_Z1 + 1)}
    if era != "2001":
        building |= annex_roof_cells()
    return _edge(terrace_cells(era), building)


def annex_roof_edge():
    cells = annex_roof_cells()
    return [c for c in _edge(cells, set()) if c != ANNEX_ROOF_STEP]


# ------------------------------------------------------------------ structure
def build_structure(m: Model, era: str) -> None:
    m.phase = "structure"
    # 主屋
    for level in ("G", "1F", "2F", "3F"):
        _build_level(m, REAR[level], D.HX0, D.HZ0, level)
    # 3階の屋根（屋上の床）と、2階の屋根（3階の南のテラス z=11..12）
    m.fill(D.HX0, D.Y_ROOF, D.HZ0, D.HX1, D.Y_ROOF, D.H3_Z1, P.TILE_WALL)
    m.fill(D.HX0 + 1, D.Y_ROOF, D.HZ0 + 1, D.HX1 - 1, D.Y_ROOF, D.H3_Z1 - 1, P.ROOF_FLOOR)
    m.fill(D.HX0, D.Y_3F, D.H3_Z1 + 1, D.HX1, D.Y_3F, D.HZ1, P.TILE_WALL)
    m.fill(D.HX0 + 1, D.Y_3F, D.H3_Z1 + 1, D.HX1 - 1, D.Y_3F, D.HZ1 - 1, P.ROOF_FLOOR)
    # 玄関ポーチのくぼみ（1階の南東角）
    px0, px1, pz0, pz1 = D.PORCH_X0, D.PORCH_X1, D.PORCH_Z0, D.PORCH_Z1
    m.fill(px0, D.Y_1F + 1, pz0, px1, D.Y_1F + 3, pz1, AIR)
    m.fill(px0, D.Y_1F, pz0, px1, D.Y_1F, pz1, B("mud_brick_slab", vhalf="bottom"))
    for z in range(pz0, pz1 + 1):
        m.fill(px0 - 1, D.Y_1F + 1, z, px0 - 1, D.Y_1F + 3, z, P.PORCH_TILE)
    for x in (px0, px1):
        m.fill(x, D.Y_1F + 1, pz0 - 1, x, D.Y_1F + 3, pz0 - 1, P.PORCH_TILE)
    m.fill(px0, D.Y_2F, pz0, px1, D.Y_2F, pz1, P.CONCRETE)  # ポーチの天井
    m.fill(px0, 1, pz0, px1, 3, pz1, P.CONCRETE)            # ポーチの下は詰める

    if era != "2001":
        build_annex_structure(m)


def build_annex_structure(m: Model) -> None:
    x0, z0 = D.AX0, D.AZ0
    _build_level(m, ANNEX["G"], x0, z0, "G")
    _build_level(m, ANNEX["1F"], x0, z0, "1F", floor_band=P.CONCRETE)  # 1階の床の帯は打ち放し
    _build_level(m, ANNEX["2F"], x0, z0, "2F", height=D.ANNEX_2F_HEIGHT)
    for z in range(z0, D.AZ1):
        for x in (D.AX0, D.AX1):
            m.set(x, D.Y_1F, z, P.TILE_WALL)
    # 地下階の正面: 柱と梁は打ち放し（シャッターは openings）
    m.fill(D.AX0, 1, D.AZ1, D.AX1, 3, D.AZ1, P.CONCRETE)
    # 主屋の南壁の上に増築棟の2階上部の北壁（y=12..13）
    yr = D.Y_ANNEX_ROOF
    m.fill(D.AX0, D.Y_3F, D.HZ1, D.AX1, yr - 1, D.HZ1, P.TILE_WALL)
    # 曲面バルコニー（屋根はかけない）
    parapet, floor = balcony_outline()
    for x, z in floor:
        m.set(x, D.Y_2F, z, P.CONCRETE)
        m.fill(x, D.Y_2F + 1, z, x, yr, z, AIR)
    for x, z in parapet:
        m.set(x, D.Y_2F, z, P.CONCRETE)
        m.set(x, D.Y_2F + 1, z, P.CONCRETE)
    # 屋根（屋上テラスの床）
    edge = set(_edge(annex_roof_cells(), set()))
    for x, z in annex_roof_cells():
        m.set(x, yr, z, P.TILE_WALL if (x, z) in edge else P.ROOF_FLOOR)


# ------------------------------------------------------------------ openings
def _window(m, x1, y1, z1, x2, y2, z2, glass=None):
    m.fill(x1, y1, z1, x2, y2, z2, glass or P.GLASS)


def _button(m, x, y, z, facing):
    m.set(x, y, z, B("stone_button", facing_direction=facing, button_pressed_bit=False))


def build_openings(m: Model, era: str) -> None:
    m.phase = "openings"
    G = P.GLASS
    L = P.GLASS_LACE
    E = D.HX1
    # ---- 主屋 ----
    # 西面 x=0
    _window(m, 0, 5, 2, 0, 6, 3, G)        # 階段室の明かり取り
    _window(m, 0, 5, 7, 0, 7, 8, L)        # リビング（縦長2連）
    _window(m, 0, 9, 9, 0, 10, 10, L)      # 寝室
    _window(m, 0, 13, 7, 0, 14, 8, L)      # 和室
    # 北面 z=0
    _window(m, 5, 6, 0, 7, 6, 0, G)        # 台所の高窓
    _window(m, 4, 10, 0, 5, 10, 0, G)      # 書斎
    _window(m, 8, 10, 0, 8, 10, 0, B("white_stained_glass_pane"))  # 浴室（型板ガラス）
    _window(m, 5, 13, 0, 7, 14, 0, G)      # 納戸
    # 東面 x=9
    _window(m, E, 5, 2, E, 6, 3, G)        # 台所
    for y in range(9, 12):                 # 浴室のガラスブロック（写真②右）
        for z in (2, 3):
            m.set(E, y, z, P.GLASS_BLOCK if (y + z) % 2 else P.GLASS_BLOCK_ALT)
    _window(m, E, 9, 9, E, 10, 10, L)      # 寝室
    _window(m, E, 13, 7, E, 14, 8, L)      # 和室
    # 3階南面 z=10（テラスへの掃き出し窓と腰窓）
    _window(m, 1, 13, 10, 1, 14, 10, L)
    _window(m, 6, 13, 10, 7, 14, 10, L)
    door(m, 3, 13, 10, "birch_door", "south", hinge=False)
    door(m, 4, 13, 10, "birch_door", "south", hinge=True)
    # 主屋の南面 z=12
    if era == "2001":
        _window(m, 1, 5, 12, 2, 7, 12, L)  # リビング（前庭向き）
        _window(m, 5, 5, 12, 6, 7, 12, L)
        _window(m, 1, 9, 12, 2, 11, 12, L)  # 寝室
        _window(m, 5, 9, 12, 6, 10, 12, L)
    else:
        for y in list(range(5, 8)) + list(range(9, 12)):
            for x in range(D.AX0 + 1, D.AX1):
                if m.get(x, y, 12) == P.TILE_WALL:
                    m.set(x, y, 12, P.WALL_INTERIOR)
        m.fill(3, 5, 12, 4, 6, 12, AIR)    # リビング → 応接室（増築棟へ）
        door(m, 3, 9, 12, "birch_door", "south")  # 寝室 → 洋室
    # 玄関ポーチの上のバルコニーへ出る扉（写真③）
    door(m, D.SX0, 9, 12, "birch_door", "south")
    # 玄関扉（グレーの金属。統合版の鉄の扉は手で開かないので、両側にボタンを付ける）
    ex, ez = D.ENTRANCE_DOOR
    door(m, ex, 5, ez, P.DOOR_ENTRANCE, "south")
    _button(m, ex + 1, 6, ez + 1, 3)
    _button(m, ex - 1, 6, ez - 1, 2)
    # 地下階 → ガレージ／駐車スペースの鉄扉
    door(m, 4, 1, 12, P.DOOR_STEEL, "south")
    _button(m, 5, 2, 13, 3)
    _button(m, 5, 2, 11, 2)

    # 室内ドア（平面図の d）
    for level, plan in REAR.items():
        f = D.LEVELS[level]
        for x, z, c in _cells(plan, D.HX0, D.HZ0):
            if c == "d":
                door(m, x, f + 1, z, P.DOOR_INTERIOR, door_facing(plan, D.HX0, D.HZ0, x, z))
                m.set(x, f + 3, z, P.WALL_INTERIOR)

    if era != "2001":
        build_annex_openings(m)


def build_annex_openings(m: Model) -> None:
    Z = D.AZ1
    # 正面: グリルシャッター（x1..5）
    for x in range(1, 6):
        for y in range(1, 4):
            m.set(x, y, Z, P.SHUTTER)
    # 1階の窓（左は細め、右は大きめ）
    _window(m, 1, 5, Z, 1, 7, Z, P.GLASS_LACE)
    _window(m, 3, 5, Z, 5, 7, Z, P.GLASS_LACE)
    # 1階 西面・東面（東面は細長いスリット窓が3本）
    _window(m, 0, 5, 15, 0, 6, 16, P.GLASS_LACE)
    for z in (14, 16, 18):
        _window(m, D.AX1, 5, z, D.AX1, 7, z, P.GLASS)
    # 2階: ルーバーの奥の背の高い窓（上はルーバーの上に見える）と、バルコニーへの扉
    _window(m, 2, 9, 18, 4, 12, 18, P.GLASS)
    m.fill(3, 9, 18, 3, 12, 18, P.WINDOW_FRAME)
    door(m, 5, 9, 18, "birch_door", "south")
    _window(m, 1, 9, 16, 1, 12, 17, P.GLASS)
    # 2階 東面: ガラスブロック（スリット窓の真上、写真①）
    for z in range(14, 17):
        for y in range(9, 12):
            m.set(D.AX1, y, z, P.GLASS_BLOCK if (y + z) % 2 else P.GLASS_BLOCK_ALT)


# ------------------------------------------------------------------ exterior details
def build_exterior(m: Model, era: str) -> None:
    m.phase = "exterior"
    E = D.HX1
    # ---- 屋上（3階の屋根）の手すり ----
    edge = []
    for x in range(D.HX0, E + 1):
        edge += [(x, D.HZ0), (x, D.H3_Z1)]
    for z in range(D.HZ0 + 1, D.H3_Z1):
        edge += [(D.HX0, z), (E, z)]
    ph = {(x, z) for x in range(0, 4) for z in range(0, 7)}  # 塔屋の位置は除く
    railing(m, [c for c in edge if c not in ph], D.Y_ROOF + 1)

    # ---- スレートの勾配屋根（3階の上端をまわる腰屋根。写真②③の濃いグレーの斜面） ----
    y = D.Y_ROOF
    slab_top = B("deepslate_tile_slab", vhalf="top")
    for z in range(D.HZ0, D.H3_Z1 + 1):
        m.set(D.HX0 - 1, y, z, stairs(P.SLATE_STAIRS, "east"))
        m.set(D.HX0 - 1, y - 1, z, slab_top)
    for x in range(D.HX0, E + 1):
        m.set(x, y, D.H3_Z1 + 1, stairs(P.SLATE_STAIRS, "north"))
        m.set(x, y, D.HZ0 - 1, stairs(P.SLATE_STAIRS, "south"))
    m.set(D.HX0 - 1, y, D.H3_Z1 + 1, P.SLATE_SLAB)
    m.set(D.HX0 - 1, y, D.HZ0 - 1, P.SLATE_SLAB)

    # ---- 3階南のテラス（2階の屋根）の手すり ----
    railing(m, terrace_edge(era), D.Y_3F + 1)

    # ---- 玄関ポーチの上のバルコニー（庇の上。写真③の縦格子） ----
    sx0, sx1 = D.SX0, D.SX1
    m.fill(sx0, D.Y_2F, D.HZ1 + 1, sx1, D.Y_2F, D.HZ1 + 2, P.CONCRETE)
    railing(m, [(sx0, D.HZ1 + 2), (sx1, D.HZ1 + 2), (sx1, D.HZ1 + 1)], D.Y_2F + 1)

    # ---- 縦樋 ----
    for (x, z, y0, y1) in [(-1, 0, 5, 14), (E + 1, 0, 6, 15), (-1, 12, 5, 11)]:
        m.fill(x, y0, z, x, y1, z, P.DOWNPIPE)

    if era != "2001":
        build_annex_exterior(m)


def build_annex_exterior(m: Model) -> None:
    parapet, floor = balcony_outline()
    # 曲面に沿った赤茶色の縦ルーバー（手すり壁の上、2段。その上に2階の窓の上端が見える）
    for x, z in parapet:
        for y in range(D.Y_2F + 2, D.Y_2F + 4):
            m.set(x, y, z, P.LOUVER)
    # 増築棟の屋上の手すりと、テラスから上がる階段
    yr = D.Y_ANNEX_ROOF
    railing(m, annex_roof_edge(), yr + 1)
    sx, sz = ANNEX_ROOF_STEP
    m.set(sx, yr, sz, stairs("polished_andesite_stairs", "south"))
    # 1階の床の帯（ガレージの上の庇）
    m.fill(D.AX0, D.Y_1F, D.APRON_Z, D.AX1, D.Y_1F, D.APRON_Z, P.CONCRETE_SLAB_TOP)
    # 打ち放しの雨だれ（ごく少量）
    for x, y in [(0, 2), (6, 3), (7, 1)]:
        m.set(x, y, D.AZ1, P.CONCRETE_STAIN)
    # セパ穴（打ち放しの柱）
    for x, y in [(6, 1), (7, 2)]:
        _button(m, x, y, D.AZ1 + 1, 3)
    # 防犯カメラ2台（シャッターの右上）
    m.set(6, 3, D.AZ1 + 1, B("lightning_rod", facing_direction=3, powered_bit=False))
    m.set(7, 3, D.AZ1 + 1, B("lightning_rod", facing_direction=3, powered_bit=False))
    # 正面右端の縦樋（写真①）
    m.fill(D.AX1 + 1, 4, D.AZ1, D.AX1 + 1, yr, D.AZ1, P.DOWNPIPE)
    # シャッターの奥は暗く
    m.fill(1, 1, D.AZ1 - 1, 5, 3, D.AZ1 - 1, AIR)
