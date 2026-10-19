"""Personagens: sprites do mapa (Joaquim e pai) e retratos 48x48 com emoções."""
import numpy as np
from paint import canvas, put, shade_px, outline, vnoise, hexc, ramp

SKIN = ramp('b07058', 'd9a283', 'f2c9a6', 'fde2c8')
HAIR = ramp('140a06', '24150e', '3a2418', '563622', '7a5038')
SHIRT = ramp('b8a882', 'd8caa6', 'f3ead2', 'fffaf0')

INK = hexc('2a1a14')
BROW = hexc('24150e')
LIP = hexc('9a4a44')
MOUTH_IN = hexc('6a2228')
TONGUE = hexc('e0707a')
TEETH = hexc('fff6ec')
WHITE = np.ones(3)
TEAR = (hexc('7ac8f0'), hexc('d8f2ff'), hexc('3a7ab0'))
EYES = (16.5, 30.5)


def fringe_y(x):
    return 21 + (1 if (x // 3) % 2 else 0) + (1 if x % 7 == 3 else 0)


def base_joaquim():
    S = 48
    c = canvas(S, S)
    L = np.array([-0.55, -0.75])
    for y in range(38, S):
        for x in range(S):
            if y < 42 and 19 <= x <= 28:
                shade_px(c, x, y, SKIN, 0.3)
            elif y >= 41:
                w = 13 + (y - 41) * 2.2
                if abs(x - 23.5) <= w:
                    v = 0.6 - abs(x - 23.5) / 40
                    if abs(x - 23.5) < 6 and y < 44:
                        v = 0.15
                    shade_px(c, x, y, SHIRT, v, dither=0.3)
    for (bx, by) in ((15, 46), (31, 45)):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 1), (1, 1)):
            put(c, bx + dx, by + dy, hexc('3a6ad0'))
    for ex in (8, 39):
        for y in range(25, 32):
            for x in range(ex - 2, ex + 3):
                if ((x - ex) / 2.6) ** 2 + ((y - 28.5) / 3.6) ** 2 <= 1:
                    shade_px(c, x, y, SKIN, 0.35 if ex < 20 else 0.55)
    cx, cy, rx, ry = 23.5, 27.5, 15.5, 14.5
    for y in range(S):
        for x in range(S):
            dx, dy = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            d = dx * dx + dy * dy
            if d > 1:
                continue
            lam = 0.35 + 0.27 * (-(dx * L[0] + dy * L[1])) + np.sqrt(1 - d) * 0.4
            shade_px(c, x, y, SKIN, np.clip(lam, 0, 1), dither=0.25)
    hx, hy, hrx, hry = 23.5, 19.5, 18.5, 16
    for y in range(S):
        for x in range(S):
            dx, dy = (x + .5 - hx) / hrx, (y + .5 - hy) / hry
            if dx * dx + dy * dy > 1:
                continue
            side = abs(x + .5 - hx) > 13.5
            if y > fringe_y(x) and not (side and y < 31 - abs(x + .5 - hx) * 0.15):
                continue
            v = 0.45 + (vnoise(x * 1.1, y * 0.18, 4) - 0.5) * 0.6 - dy * 0.15 - dx * 0.1
            if abs((y - 10) - (dx * dx) * 6) < 1.6 and -0.75 < dx < 0.2:
                v += 0.45
            if y >= fringe_y(x) - 1:
                v -= 0.25
            shade_px(c, x, y, HAIR, np.clip(v, 0, 1), dither=0.4)
    for x in range(10, 38):
        put(c, x, fringe_y(x) + 1, SKIN[1])
    put(c, 24, 31, SKIN[1]); put(c, 23, 32, SKIN[1]); put(c, 24, 32, SKIN[0])
    return c


# ------------------------------------------------------------ partes do rosto

def blush(c, strong=False):
    for bx in (13.5, 33.5):
        for y in range(30, 36):
            for x in range(int(bx - 4), int(bx + 5)):
                inside = ((x + .5 - bx) / 3.6) ** 2 + ((y + .5 - 32.8) / 2.2) ** 2 <= 1
                if inside and (strong or (x + y) % 2 == 0):
                    put(c, x, y, hexc('ef9e8c') if not strong else hexc('f08a80'))


def brows(c, outer, inner, arch):
    """outer/inner = altura (y) das pontas de fora e de dentro."""
    for (x_out, x_in) in ((13, 20), (34, 27)):
        n = abs(x_in - x_out)
        for i in range(n + 1):
            t = i / n
            x = x_out + (i if x_in > x_out else -i)
            y = round(outer + (inner - outer) * t - np.sin(t * np.pi) * arch)
            put(c, x, y, BROW)
            if 0.1 < t < 0.92:
                put(c, x, y + 1, hexc('3a2418'))


def eye_open(c, ex, cy=28.4, rx=2.4, ry=2.6, look=0):
    for y in range(24, 33):
        for x in range(int(ex - 4), int(ex + 4)):
            if ((x + .5 - ex) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1:
                put(c, x, y, INK)
    put(c, int(ex) - 1 + look, int(cy) - 1, WHITE)
    put(c, int(ex) + look, int(cy) - 1, WHITE * .85)
    put(c, int(ex) + 1 + look, int(cy) + 1, hexc('5a3a2a'))


def eye_wide(c, ex):
    for y in range(24, 33):
        for x in range(int(ex - 4), int(ex + 4)):
            d = ((x + .5 - ex) / 2.9) ** 2 + ((y + .5 - 28.2) / 3.1) ** 2
            if d <= 1:
                put(c, x, y, INK if d > .62 else WHITE)
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            put(c, int(ex) + dx, 28 + dy, INK)
    put(c, int(ex) - 1, 27, WHITE)


def eye_happy(c, ex):
    """olho fechado em arco ^ (risada)."""
    for x in range(int(ex - 3), int(ex + 3)):
        t = (x + .5 - ex) / 2.8
        y = 29 - round((1 - t * t) * 1.8)
        put(c, x, y, INK)
        put(c, x, y + 1, INK if abs(t) < .5 else SKIN[1])


def lid(c, ex, top_left, top_right):
    """pálpebra cobrindo o topo do olho (linha inclinada)."""
    for x in range(int(ex - 3), int(ex + 3)):
        t = (x - (ex - 3)) / 6
        ly = round(top_left + (top_right - top_left) * t)
        for y in range(25, ly):
            put(c, x, y, SKIN[2] if y < ly - 1 else SKIN[1])
        put(c, x, ly, INK)


def lower_smile_lid(c, ex):
    for x in range(int(ex - 2), int(ex + 3)):
        put(c, x, 31, SKIN[1])


def curve(c, x0, x1, ybase, bend, col):
    """linha da boca: bend>0 sorri (centro desce), bend<0 fica triste."""
    pts = []
    for x in range(x0, x1 + 1):
        t = (x - (x0 + x1) / 2) / ((x1 - x0) / 2)
        y = ybase + round((1 - t * t) * bend)
        put(c, x, y, col)
        pts.append((x, y))
    return pts


def mouth_soft(c):
    for x, y in curve(c, 18, 29, 35, 1.6, LIP):
        t = (x - 23.5) / 6
        if abs(t) < .55:
            put(c, x, y + 1, SKIN[1])
    put(c, 17, 34, SKIN[1]); put(c, 30, 34, SKIN[1])


def mouth_neutral(c):
    for x in range(20, 28):
        put(c, x, 36, LIP)
    put(c, 21, 37, SKIN[1]); put(c, 22, 37, SKIN[1]); put(c, 25, 37, SKIN[1])


def mouth_big(c):
    """boca aberta de alegria (formato D), com língua."""
    for x in range(18, 30):
        t = (x - 23.5) / 6
        bot = 35 + round((1 - t * t) * 3.4)
        for y in range(35, bot + 1):
            if y == 35:
                col = LIP
            elif y == 36 and abs(t) < .75:
                col = TEETH
            elif y == bot:
                col = LIP
            elif y >= bot - 1 and abs(t) < .45:
                col = TONGUE
            else:
                col = MOUTH_IN
            put(c, x, y, col)


def mouth_o(c, rx=2.2, ry=2.6, cy=36.5):
    for y in range(32, 41):
        for x in range(18, 30):
            d = ((x + .5 - 23.5) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2
            if d <= 1:
                put(c, x, y, LIP if d > .5 else MOUTH_IN)


def mouth_frown(c):
    curve(c, 19, 28, 37, -1.4, LIP)
    put(c, 23, 38, SKIN[1]); put(c, 24, 38, SKIN[1])


def mouth_pout(c):
    for x in range(20, 27):
        put(c, x, 36, LIP)
    put(c, 27, 37, LIP); put(c, 19, 36, SKIN[1])
    put(c, 22, 37, SKIN[1]); put(c, 23, 37, SKIN[1])


def mouth_grit(c):
    for y in range(34, 39):
        for x in range(18, 30):
            edge = y in (34, 38) or x in (18, 29)
            if edge:
                put(c, x, y, LIP)
            else:
                put(c, x, y, TEETH if y != 36 else hexc('b8a8a0'))
                if (x - 18) % 3 == 0 and y != 36:
                    put(c, x, y, hexc('d8ccc4'))


def mouth_wavy(c):
    for x in range(19, 29):
        put(c, x, 36 + (x % 2), LIP)


# ------------------------------------------------------------ extras

def tear(c, x=14, y0=31):
    for i, y in enumerate(range(y0, y0 + 4)):
        put(c, x, y, TEAR[0])
    put(c, x, y0 + 4, TEAR[2]); put(c, x - 1, y0 + 3, TEAR[0]); put(c, x + 1, y0 + 3, TEAR[0])
    put(c, x - 1, y0 + 4, TEAR[2]); put(c, x + 1, y0 + 4, TEAR[2]); put(c, x, y0 + 1, TEAR[1])


def sweat(c, x=40, y=19):
    shape = ["..a..", ".aba.", "abbba", "abcba", ".aaa."]
    cols = {'a': TEAR[2], 'b': TEAR[0], 'c': TEAR[1]}
    for dy, row in enumerate(shape):
        for dx, ch in enumerate(row):
            if ch != '.':
                put(c, x + dx - 2, y + dy, cols[ch])


def anger_mark(c, x=37, y=9):
    red, dark = hexc('e8404a'), hexc('8a1a24')
    for i in range(-3, 4):
        if abs(i) > 0:
            for (px, py) in ((x + i, y - 2), (x + i, y + 2), (x - 2, y + i), (x + 2, y + i)):
                if abs(px - x) >= 1 and abs(py - y) >= 1:
                    put(c, px, py, red)
    for (px, py) in ((x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)):
        put(c, px, py, dark)


def sparkle(c, x, y, big=True):
    col, core = hexc('ffe27a'), WHITE
    r = 3 if big else 2
    for i in range(-r, r + 1):
        put(c, x + i, y, col); put(c, x, y + i, col)
    put(c, x, y, core)
    if big:
        for d in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            put(c, x + d[0], y + d[1], col)


def gloom(c):
    """linhas de "arrepio" ao lado do rosto."""
    col = hexc('8a7ab8')
    for x in (5, 41):
        for y in range(16, 23, 2):
            put(c, x, y, col)
            put(c, x + (1 if x > 20 else -1), y + 1, col)


# ------------------------------------------------------------ emoções

def normal(c):
    blush(c); brows(c, 24, 24, 1.0)
    for ex in EYES: eye_open(c, ex)
    mouth_neutral(c)


def feliz(c):
    blush(c); brows(c, 24, 24, 1.4)
    for ex in EYES:
        eye_open(c, ex); lower_smile_lid(c, ex)
    mouth_soft(c)


def animado(c):
    blush(c, strong=True); brows(c, 23, 23, 1.8)
    for ex in EYES: eye_happy(c, ex)
    mouth_big(c)
    sparkle(c, 5, 9); sparkle(c, 43, 13, big=False); sparkle(c, 40, 4, big=False)


def surpreso(c):
    blush(c); brows(c, 23, 23, 2.2)
    for ex in EYES: eye_wide(c, ex)
    mouth_o(c)


def triste(c):
    brows(c, 25, 22, 0.3)
    for ex, (l, r) in zip(EYES, ((26, 27), (27, 26))):
        eye_open(c, ex, cy=28.9, look=0)
        lid(c, ex, l + 1, r + 1) if False else None
    lid(c, EYES[0], 27, 26)
    lid(c, EYES[1], 26, 27)
    mouth_frown(c); tear(c, 14, 31)


def chateado(c):
    brows(c, 25, 25, 0)
    for ex in EYES:
        eye_open(c, ex, look=1)
        lid(c, ex, 28, 28)
    mouth_pout(c)
    sweat(c, 41, 20)


def raiva(c):
    blush(c, strong=True); brows(c, 22, 26, 0)
    for ex, (l, r) in zip(EYES, ((27, 28), (28, 27))):
        eye_open(c, ex, cy=29, ry=2.1)
    lid(c, EYES[0], 27, 28)
    lid(c, EYES[1], 28, 27)
    mouth_grit(c); anger_mark(c, 37, 9)


def medo(c):
    brows(c, 25, 22, 0.5)
    for ex in EYES: eye_wide(c, ex)
    mouth_wavy(c); sweat(c, 41, 19); sweat(c, 6, 22); gloom(c)


EMOCOES = [('Normal', normal), ('Feliz', feliz), ('Animado', animado), ('Surpreso', surpreso),
           ('Triste', triste), ('Chateado', chateado), ('Com raiva', raiva), ('Com medo', medo)]


def retrato_joaquim(fn):
    c = base_joaquim()
    fn(c)
    return outline(c, hexc('2a1810'))




# ================================================================== sprites do mapa (20x34)

JPAL = {
    'k': '2a1810', 'h': '3a2418', 'H': '6a4630', 'd': '1e110a',
    's': 'f2c9a6', 'S': 'd9a283', 'r': 'ef9e8c', 'D': '24150e',
    'E': '2a1a14', 'w': 'ffffff', 'm': '9a4a44', 't': 'fff6ec',
    'T': 'f3ead2', 'U': 'd2c39f', 'b': '3a6ad0', 'B': '24429a',
    'n': '1e2440', 'q': 'c9b98a', 'Q': 'a8966a', 'o': '3a3030', 'l': '8a8a96',
    # pai
    'P': '2a1d16', 'p': '4a3426', 'f': 'e8b896', 'F': 'c48e6c', 'G': '4a9a5a', 'g': '2f6a3e',
    'J': '3a5a8a', 'j': '2a4068', 'c': '3a2a20', 'y': '1e140e',
}

J_FRENTE = [
    "......kkkkkkkk......",
    "....kkhhhhhhhhkk....",
    "...khhhHHHhhhhhhk...",
    "..khhHHhhhhhhhhhhk..",
    "..khhhhhhhhhhhhhhk..",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhhhhhhhhhhhhk.",
    ".khdhhhdhhhdhhhdhhk.",
    ".khsdsssdssdsssdshk.",
    ".khSssssssssssssShk.",
    ".khsDDssssssssDDshk.",
    ".khsssssssssssssshk.",
    ".khsswEsssssswEsshk.",
    ".khssEEssssssEEsshk.",
    ".kssrrssssssssrrssk.",
    ".kssrsmssssssmsrssk.",
    ".kSssssmmmmmmssssSk.",
    "..kSssssssssssssSk..",
    "...kkSSssssssSSkk...",
    "....kTTkSSSSkTTk....",
    "..kkTTTTkkkkTTTTkk..",
    ".kTTTTTTTTTTTTTTTTk.",
    "kTTTTbTTTTTTTbTTTTUk",
    "ksTTTTTTbBbTTTTTTUsk",
    "ksTTTTTbBBBbTTTTTUsk",
    "ksSTTTTTbBbTTTTTUSsk",
    "kssTTTTTTTTTTTTTUssk",
    ".kkUTTTTTTTTTTTTUkk.",
    "..knnnnnnnnnnnnnnk..",
    "..kqqqqqqQqqqqqqqk..",
    "..kqqqqqkkkkqqqqqk..",
    "...ksssk....ksssk...",
    "...koook....koook...",
    "..kooolk....kooolk..",
]

J_FRENTE_PASSO = J_FRENTE[:31] + [
    "...ksssk....koook...",
    "...koook....kooolk..",
    "..kooolk............",
]

J_COSTAS = [
    "......kkkkkkkk......",
    "....kkhhhhhhhhkk....",
    "...khhhhhhhhhhhhk...",
    "..khhhhhhHHhhhhhhk..",
    "..khhhhhHHhhhhhhhk..",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhdhhhhdhhhhhk.",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhdhhhhhhhhhhdhhk.",
    ".kshhhhhhhhhhhhhhsk.",
    ".kshhhhhhhhhhhhhhsk.",
    ".kshhdhhhhhhhhdhhsk.",
    ".kShhhhhhhhhhhhhhSk.",
    "..khhhdhhhhhhdhhhk..",
    "..kkhhhhhhhhhhhhkk..",
    "...kkSSssssssSSkk...",
    "....kTTkSSSSkTTk....",
    "..kkTTTTTTTTTTTTkk..",
    ".kTTTTTTTTTTTTTTTTk.",
    "kTTTTTTTTTTTTTTTTTUk",
    "ksTTTTTTTTTTTTTTTUsk",
    "ksTTTTTTTTTTTTTTTUsk",
    "ksSTTTTTTTTTTTTTUSsk",
    "kssTTTTTTTTTTTTTUssk",
    ".kkUTTTTTTTTTTTTUkk.",
    "..knnnnnnnnnnnnnnk..",
    "..kqqqqqqQqqqqqqqk..",
    "..kqqqqqkkkkqqqqqk..",
    "...ksssk....ksssk...",
    "...koook....koook...",
    "..kooolk....kooolk..",
]
J_COSTAS_PASSO = J_COSTAS[:-3] + J_FRENTE_PASSO[-3:]

J_LADO = [
    "......kkkkkkk.......",
    "....kkhhhhhhhkk.....",
    "...khhhHHHhhhhhk....",
    "..khhHHhhhhhhhhhk...",
    "..khhhhhhhhhhhhhhk..",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhhhhhhhhhhhhk.",
    ".khhhhhhhhhdhhdhhhk.",
    ".khhhhhhhhdssdssdhk.",
    ".khhhhhhhhSsssssssk.",
    ".khhhhhhhssssDDsssk.",
    ".khhhhhhSSssssssssk.",
    ".khhhhhhSkSssswEssk.",
    ".khhhhhhSSssssEEssk.",
    ".khhhhhhhssssrssssk.",
    ".kShhhhhSsssssssmsk.",
    "..kShhhSsssssmmmsk..",
    "...kkSSsssssssSkk...",
    ".....kTTkSSSkTTk....",
    "....kkTTTTkkTTTkk...",
    "....kTTTTTTTTTTTk...",
    "...kTTTTTTTTTTTTUk..",
    "...kTTTTkssskTTTUk..",
    "...kTTTTkssskTTTUk..",
    "...kTTTTksSskTTTUk..",
    "...kUTTTkssskTTUUk..",
    "...kUTTTTkkkTTTUUk..",
    "....kUTTTTTTTTUk....",
    "....knnnnnnnnnnk....",
    "....kqqqqqqqqqqk....",
    "....kqqqqqkqqqqk....",
    ".....ksssk.ksssk....",
    ".....koook.koook....",
    ".....kooolkkooolk...",
]

J_LADO_PASSO = J_LADO[:31] + [
    "....ksssk...ksssk...",
    "...koook.....koook..",
    "..kooolk.....kooolk.",
]

PAI = [
    ".......kkkkkkkk.......",
    ".....kkPPPPPPPPkk.....",
    "....kPPPPpppPPPPPk....",
    "...kPPPppppppppPPPk...",
    "...kPPfffffffffffPk...",
    "...kPfffffffffffffk...",
    "...kffyyyfffffyyyffk..",
    "...kfffwEffffffwEffk..",
    "..kFfffEEffffffEEfffk.",
    "..kFffffffFFffffffffk.",
    "...kfffPPPPPPPPPfffk..",
    "...kffffPmmmmPffffk...",
    "....kFffffffffffFk....",
    ".....kkFFffffFFkk.....",
    "......kGGkFFkGGk......",
    "....kkGGGGkkGGGGkk....",
    "...kGGGGGGGGGGGGGGk...",
    "..kGGGGGGGGGGGGGGGGk..",
    ".kgGGGGGGGGGGGGGGGGgk.",
    ".kfgGGGGGGGGGGGGGGgfk.",
    ".kfgGGGGGGGGGGGGGGgfk.",
    ".kfgGGGGGGGGGGGGGGgfk.",
    ".kffgGGGGGGGGGGGGgffk.",
    ".kffgGGGGGGGGGGGGgffk.",
    "..kkgGGGGGGGGGGGGgkk..",
    "...kccccccccccccccck..",
    "...kJJJJJJJJJJJJJJk...",
    "...kJJJJJJjJJJJJJJk...",
    "...kJJJJJJkkJJJJJJk...",
    "...kJJJJJk..kJJJJJk...",
    "...kJJJJJk..kJJJJJk...",
    "...kJJJJJk..kJJJJJk...",
    "...kjJJJJk..kJJJJjk...",
    "...kJJJJJk..kJJJJJk...",
    "...kJJJJJk..kJJJJJk...",
    "...kjJJJJk..kJJJJjk...",
    "...koooook..koooook...",
    "...kkkkkkk..kkkkkkk...",
]


def grid(rows, width):
    for i, r in enumerate(rows):
        assert len(r) == width, (i, len(r), r)
    c = canvas(width, len(rows))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.':
                put(c, x, y, hexc(JPAL[ch]))
    return c


def sprites_joaquim():
    s = {
        'joaquim_baixo0': grid(J_FRENTE, 20),
        'joaquim_baixo1': grid(J_FRENTE_PASSO, 20),
        'joaquim_cima0': grid(J_COSTAS, 20),
        'joaquim_cima1': grid(J_COSTAS_PASSO, 20),
        'joaquim_lado0': grid(J_LADO, 20),
        'joaquim_lado1': grid(J_LADO_PASSO, 20),
    }
    s['joaquim_deitado'] = np.rot90(s['joaquim_baixo0'], 1).copy()
    return s


def sprite_pai():
    return grid(PAI, 22)


# ================================================================== retrato do pai

PSKIN = ramp('a86a50', 'c48e6c', 'e8b896', 'f8d4b4')
PHAIR = ramp('100806', '1e140e', '2a1d16', '4a3426', '6a4a36')
PSHIRT = ramp('1e4a2a', '2f6a3e', '4a9a5a', '6ab878')


def base_pai():
    S = 48
    c = canvas(S, S)
    L = np.array([-0.55, -0.75])
    for y in range(38, S):
        for x in range(S):
            if y < 42 and 19 <= x <= 28:
                shade_px(c, x, y, PSKIN, 0.3)
            elif y >= 40:
                w = 15 + (y - 40) * 2.2
                if abs(x - 23.5) <= w:
                    v = 0.55 - abs(x - 23.5) / 40
                    collar = abs(x - 23.5) < 7 - (y - 40) and y < 45
                    shade_px(c, x, y, PSHIRT if not collar else PSHIRT, 0.85 if collar else v, dither=0.3)
    for ex in (8, 39):
        for y in range(24, 32):
            for x in range(ex - 2, ex + 3):
                if ((x - ex) / 2.6) ** 2 + ((y - 28) / 3.8) ** 2 <= 1:
                    shade_px(c, x, y, PSKIN, 0.35 if ex < 20 else 0.55)
    cx, cy, rx, ry = 23.5, 26.5, 15, 15.5
    for y in range(S):
        for x in range(S):
            dx, dy = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            d = dx * dx + dy * dy
            if d > 1:
                continue
            lam = 0.35 + 0.27 * (-(dx * L[0] + dy * L[1])) + np.sqrt(1 - d) * 0.4
            shade_px(c, x, y, PSKIN, np.clip(lam, 0, 1), dither=0.25)
    # cabelo curto com risca de lado
    hx, hy, hrx, hry = 23.5, 16, 17, 12
    for y in range(S):
        for x in range(S):
            dx, dy = (x + .5 - hx) / hrx, (y + .5 - hy) / hry
            if dx * dx + dy * dy > 1:
                continue
            hairline = 17 + abs(x + .5 - 23.5) * 0.18 + (2 if x < 17 else 0)
            side = abs(x + .5 - hx) > 13.5 and y < 27
            if y > hairline and not side:
                continue
            v = 0.45 + (vnoise(x * .35, y * .9, 8) - .5) * .5 - dy * .1
            if x == 17 and y < 14:
                v = 0.1  # risca
            if abs((y - 8) - (dx * dx) * 5) < 1.4 and 0.0 < dx < 0.7:
                v += 0.4
            shade_px(c, x, y, PHAIR, np.clip(v, 0, 1), dither=0.4)
    put(c, 24, 31, PSKIN[1]); put(c, 23, 32, PSKIN[1]); put(c, 24, 32, PSKIN[0])
    return c


def bigode(c):
    for x in range(16, 32):
        t = (x - 23.5) / 8
        for y in range(33, 35 + (1 if abs(t) > .55 else 0)):
            shade_px(c, x, y, PHAIR, 0.45 - abs(t) * 0.2 + (0.15 if y == 33 else 0))


def pai_normal(c):
    brows(c, 23, 23, 0.6)
    for ex in EYES: eye_open(c, ex)
    for x in range(20, 28):
        put(c, x, 36, LIP)
    bigode(c)


def pai_feliz(c):
    brows(c, 23, 23, 1.2)
    for ex in EYES:
        eye_open(c, ex); lower_smile_lid(c, ex)
    curve(c, 18, 29, 35, 1.8, LIP)
    bigode(c)


def retrato_pai(fn):
    c = base_pai()
    fn(c)
    return outline(c, hexc('1e1410'))
