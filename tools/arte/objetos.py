"""Objetos do cenário: árvores, arbustos, cerca, poste, móveis, coisas da floresta."""
import numpy as np
from paint import (R, ramp, canvas, put, shade_px, outline, blob, vnoise, hash2, hexc)

LEAF_MATA = ramp('0c1c1a', '12302a', '1a4434', '24583c', '347044', '4e8c4c')


def arvore(w=52, h=70, s=1, folhas=None, luz=(0.55, -0.8)):
    c = canvas(w, h)
    leaf = folhas if folhas is not None else R['leaf']
    tx = w // 2
    for y in range(int(h * 0.55), h):
        spread = 0 if y < h - 4 else (y - (h - 4))
        for x in range(tx - 3 - spread, tx + 4 + spread):
            shade_px(c, x, y, R['bark'], 0.3 + 0.45 * ((x - tx + 3) / 7) + (vnoise(x * .5, y * .2, s) - .5) * .4)
    rng = np.random.default_rng(s)
    clusters = [(w * 0.5, h * 0.36, w * 0.36)]
    for _ in range(7):
        a = rng.uniform(0, 2 * np.pi)
        clusters.append((w * 0.5 + np.cos(a) * w * 0.22, h * 0.36 + np.sin(a) * h * 0.18, w * rng.uniform(0.17, 0.24)))
    clusters.sort(key=lambda k: k[1])
    for i, (cx, cy, r) in enumerate(clusters):
        blob(c, cx, cy, r, leaf, light=luz, s=s * 10 + i, base=0.15 - (cy / h) * 0.25)
    return outline(c, (0.05, 0.08, 0.07))


def arvore_mata(s=1):
    """Árvore grande e escura da floresta densa."""
    return arvore(64, 96, s=s, folhas=LEAF_MATA, luz=(0.3, -0.9))


def arbusto(w=26, h=16, s=4, flores=True):
    c = canvas(w, h)
    for i, (cx, cy, r) in enumerate([(7, 10, 6.5), (19, 10, 6.5), (13, 7, 7)]):
        blob(c, cx, cy, r, R['leaf'], light=(0.55, -0.8), s=s + i, base=0.05)
    if flores:
        rng = np.random.default_rng(s)
        for _ in range(6):
            put(c, rng.integers(3, w - 3), rng.integers(3, h - 4), R['pink'][rng.integers(2, 4)])
    return outline(c, (0.05, 0.08, 0.07))


def cerca():
    """Um trecho de cerca de 1 tile (16 px), emenda com os vizinhos."""
    W, H = 16, 18
    c = canvas(W, H)
    for x in range(W):
        for y in (5, 6, 11, 12):
            shade_px(c, x, y, R['wood'], 0.75 if y in (5, 11) else 0.45)
    for x0 in (2, 10):
        for y in range(1, H):
            for dx in range(3):
                shade_px(c, x0 + dx, y, R['wood'], [0.8, 0.6, 0.35][dx] - (0.15 if y > H - 4 else 0))
        put(c, x0 + 1, 0, R['wood'][3])
    return outline(c, (0.12, 0.07, 0.05))


def poste():
    W, H = 10, 46
    c = canvas(W, H)
    for y in range(12, H):
        for x in (4, 5):
            shade_px(c, x, y, R['iron'], 0.7 if x == 4 else 0.35)
    for x in range(2, 8):
        shade_px(c, x, H - 2, R['iron'], 0.5)
        shade_px(c, x, H - 1, R['iron'], 0.3)
    for y in range(2, 12):
        for x in range(1, 9):
            if y in (2, 11) or x in (1, 8):
                shade_px(c, x, y, R['iron'], 0.6)
            else:
                shade_px(c, x, y, R['yellow'], 0.95 - abs(x - 4.5) * 0.08)
    put(c, 4, 0, R['iron'][2]); put(c, 5, 0, R['iron'][2])
    for x in range(2, 8):
        put(c, x, 1, R['iron'][1])
    return outline(c)


# ------------------------------------------------------------------ casa

FABRIC = ramp('4a1420', '7a2430', 'a8384a', 'c85a5a', 'e08070')
METAL = ramp('1a1c24', '2c303c', '444a58', '6a7282')


def poltrona():
    W, H = 20, 20
    c = canvas(W, H)
    for y in range(H):
        for x in range(W):
            back = 2 <= x <= 17 and 1 <= y <= 11
            seat = 1 <= x <= 18 and 10 <= y <= 15
            arm = (x <= 3 or x >= 16) and 6 <= y <= 15
            leg = y >= 16 and (x in (2, 3, 16, 17))
            if leg:
                shade_px(c, x, y, R['wood'], 0.3)
            elif arm:
                shade_px(c, x, y, FABRIC, 0.55 - (y - 6) * 0.02 + (0.15 if x in (1, 16) else 0))
            elif seat:
                shade_px(c, x, y, FABRIC, 0.65 - (y - 10) * 0.08)
            elif back:
                v = 0.45 + (0.15 if y < 3 else 0) - abs(x - 9.5) * 0.01
                if x in (6, 13):
                    v -= 0.2  # botões/costura
                shade_px(c, x, y, FABRIC, v)
    return outline(c)


def mesinha():
    """Mesinha com abajur aceso."""
    W, H = 16, 24
    c = canvas(W, H)
    for y in range(12, H):
        for x in range(W):
            if y in (12, 13) and 0 <= x < 16:
                shade_px(c, x, y, R['wood'], 0.75 if y == 12 else 0.5)
            elif y > 13 and x in (2, 3, 12, 13):
                shade_px(c, x, y, R['wood'], 0.35)
            elif y == 19 and 3 < x < 12:
                shade_px(c, x, y, R['wood'], 0.4)
    # abajur
    for y in range(0, 7):
        hw = 2 + y * 0.6
        for x in range(int(8 - hw), int(8 + hw)):
            shade_px(c, x, y + 1, R['yellow'], 0.9 - y * 0.06)
    for y in range(8, 12):
        put(c, 7, y, R['iron'][2]); put(c, 8, y, R['iron'][1])
    for x in range(5, 11):
        put(c, x, 11, R['iron'][1])
    return outline(c)


def tv():
    W, H = 18, 20
    c = canvas(W, H)
    for y in range(1, 13):
        for x in range(1, 17):
            if y in (1, 12) or x in (1, 16):
                shade_px(c, x, y, METAL, 0.3)
            elif 2 < x < 15 and 2 < y < 11:
                v = 0.35 + (0.4 if (x - y) in (2, 3) else 0) + (y % 2) * 0.05
                shade_px(c, x, y, ramp('0e1a30', '1e3a6a', '3a6ab0', '8ac0f0'), v)
            else:
                shade_px(c, x, y, METAL, 0.6)
    for y in range(13, H):
        for x in range(3, 15):
            if y == 13 or y == H - 1 or x in (3, 14):
                shade_px(c, x, y, R['wood'], 0.3)
            else:
                shade_px(c, x, y, R['wood'], 0.55 if y < 16 else 0.45)
    put(c, 13, 11, R['red'][2])
    return outline(c)


def planta():
    W, H = 16, 24
    c = canvas(W, H)
    rng = np.random.default_rng(5)
    for i in range(9):
        a = -np.pi / 2 + rng.uniform(-1.1, 1.1)
        L = rng.uniform(7, 12)
        for t in np.linspace(0, 1, 18):
            x = 8 + np.cos(a) * L * t + np.sin(t * 3) * 0.6
            y = 14 + np.sin(a) * L * t + t * t * 3
            shade_px(c, int(x), int(y), R['leaf'], 0.35 + t * 0.5)
            shade_px(c, int(x) + 1, int(y), R['leaf'], 0.25 + t * 0.4)
    for y in range(14, H):
        hw = 5 - (y - 14) * 0.2
        for x in range(int(8 - hw), int(8 + hw)):
            shade_px(c, x, y, ramp('5a2a1a', '8a4a2a', 'b8683a', 'd88a5a'), 0.6 - (x - 8 + hw) / (2 * hw) * 0.4 - (0.2 if y == 14 else 0))
    return outline(c)


BLANKET = ramp('1a2a5a', '24429a', '3a6ad0', '6a9ae8', 'a8c8f8')


def cama_topo(dormindo=False):
    """Colchão visto de cima: 1 tile de largura x 2 de comprimento (travesseiro no fundo)."""
    W, H = 16, 32
    c = canvas(W, H)
    for y in range(H):
        for x in range(W):
            if x in (0, W - 1):
                shade_px(c, x, y, R['wood'], 0.4)
            elif y < 9:
                v = 0.85 if 2 <= x <= 13 and 1 <= y <= 7 else 0.6
                shade_px(c, x, y, R['white'], v - (0.2 if y == 7 else 0))
            else:
                v = 0.5 + 0.15 * np.sin((x + y) * 0.9) * 0.5 + (0.2 if y == 9 else 0)
                if (x + y) % 6 == 0:
                    v += 0.2
                shade_px(c, x, y, BLANKET, v)
    if dormindo:
        from personagens import HAIR, SKIN
        # cabeça no travesseiro
        for y in range(1, 10):
            for x in range(3, 13):
                if ((x + .5 - 8) / 4.6) ** 2 + ((y + .5 - 5.5) / 4.2) ** 2 <= 1:
                    hair = y < 5 or x in (3, 12)
                    shade_px(c, x, y, HAIR if hair else SKIN, 0.55 if hair else 0.6)
        for x in (6, 9):
            put(c, x, 6, hexc('2a1a14'))  # olhos fechados
        put(c, 7, 8, hexc('9a4a44')); put(c, 8, 8, hexc('9a4a44'))
        # corpo embaixo da coberta
        for y in range(10, 28):
            for x in range(3, 13):
                if ((x + .5 - 8) / 5.2) ** 2 + ((y - 18) / 9.5) ** 2 <= 1:
                    shade_px(c, x, y, BLANKET, 0.75 - abs(x - 8) * 0.06)
    return c


def cama_frente():
    W, H = 16, 8
    c = canvas(W, H)
    for y in range(H):
        for x in range(W):
            if y < 3:
                shade_px(c, x, y, BLANKET, 0.4 - y * 0.1)
            else:
                shade_px(c, x, y, R['wood'], 0.55 if y == 3 else 0.35)
    return c


def cama_cabeceira():
    W, H = 18, 22
    c = canvas(W, H)
    for y in range(H):
        for x in range(W):
            top = 3 - int(3 * np.sqrt(max(0, 1 - ((x - 8.5) / 9) ** 2)))
            if y < top:
                continue
            v = 0.55 + (vnoise(x * .3, y * .1, 2) - .5) * .3
            if x in (0, 1, W - 2, W - 1):
                v = 0.3
            if y == top:
                v = 0.8
            shade_px(c, x, y, R['wood'], v)
    return outline(c)


# ------------------------------------------------------------------ floresta

def capim(s=0):
    W, H = 16, 12
    c = canvas(W, H)
    rng = np.random.default_rng(s)
    for i in range(9):
        x0 = rng.integers(1, 15)
        hgt = rng.integers(5, 12)
        lean = rng.uniform(-0.35, 0.35)
        for k in range(hgt):
            x = int(x0 + lean * k)
            shade_px(c, x, H - 1 - k, R['grass'], 0.25 + k / hgt * 0.6)
    return c


def cogumelo():
    W, H = 12, 10
    c = canvas(W, H)
    for (cx, cy, r, st) in ((4, 4, 3.4, 9), (8.5, 6, 2.4, 9)):
        for y in range(H):
            for x in range(W):
                if y < cy and ((x + .5 - cx) / r) ** 2 + ((y + .5 - cy) / (r * .8)) ** 2 <= 1:
                    v = 0.75 - (y - (cy - r)) * 0.08
                    shade_px(c, x, y, R['red'], v)
        for y in range(int(cy), st):
            put(c, int(cx), y, R['white'][2]); put(c, int(cx) - 1, y, R['white'][1])
        put(c, int(cx) - 1, int(cy - r * .5), R['white'][3])
        put(c, int(cx) + 1, int(cy - 1), R['white'][3])
    return outline(c)


def tronco():
    W, H = 32, 14
    c = canvas(W, H)
    for y in range(3, 13):
        for x in range(1, 31):
            v = 0.55 - abs(y - 6) * 0.06 + (vnoise(x * .4, y * .4, 3) - .5) * .3
            if x > 27:
                ring = np.hypot(x - 28, y - 7.5)
                shade_px(c, x, y, R['dirt'], 0.8 - (ring % 2) * 0.3)
                continue
            shade_px(c, x, y, R['bark'], v)
    for x in range(4, 26, 5):  # musgo
        put(c, x, 3, R['leaf'][4]); put(c, x + 1, 3, R['leaf'][3]); put(c, x, 4, R['leaf'][3])
    return outline(c)


# ------------------------------------------------------------------ efeitos e ícones

def brilho(grande):
    c = canvas(15, 15)
    if not grande:
        for (x, y) in ((7, 7), (6, 7), (8, 7), (7, 6), (7, 8)):
            put(c, x, y, np.array([1, .97, .8]))
        put(c, 7, 7, np.ones(3))
        return c
    for i in range(15):
        a = 1 - abs(i - 7) / 7.5
        put(c, 7, i, np.array([1, 0.97, 0.8]), a)
        put(c, i, 7, np.array([1, 0.97, 0.8]), a)
    for i in range(-2, 3):
        put(c, 7 + i, 7 + i, np.array([1, 1, 0.9]), 0.7)
        put(c, 7 + i, 7 - i, np.array([1, 1, 0.9]), 0.7)
    put(c, 7, 7, np.ones(3))
    return c


def exclamacao():
    rows = [
        "..kkkkkk..",
        ".kwwwwwwk.",
        "kwwwrrwwwk",
        "kwwwrrwwwk",
        "kwwwrrwwwk",
        "kwwwrrwwwk",
        "kwwwwwwwwk",
        "kwwwrrwwwk",
        ".kwwwwwwk.",
        "..kkwwkk..",
        "....kk....",
    ]
    col = {'k': hexc('1a1c2c'), 'w': np.ones(3), 'r': hexc('d04040')}
    c = canvas(10, len(rows))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                put(c, x, y, col[ch])
    return c


def sombra():
    """Elipse suave para sombras no chão (usada com filtro bilinear)."""
    S = 32
    c = canvas(S, S)
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.hypot((xx + .5 - S / 2) / (S / 2), (yy + .5 - S / 2) / (S / 2))
    c[:, :, :3] = 0
    c[:, :, 3] = np.clip(1 - d, 0, 1) ** 1.4
    return c


def luz():
    S = 64
    c = canvas(S, S)
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.hypot((xx + .5 - S / 2) / (S / 2), (yy + .5 - S / 2) / (S / 2))
    c[:, :, :3] = 1
    c[:, :, 3] = np.exp(-(d * 2.2) ** 2) * (d < 1)
    return c


def pontinho():
    """Partícula (pólen, poeira, vaga-lume)."""
    S = 8
    c = canvas(S, S)
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.hypot(xx + .5 - S / 2, yy + .5 - S / 2) / (S / 2)
    c[:, :, :3] = 1
    c[:, :, 3] = np.clip(1 - d, 0, 1) ** 1.5
    return c


def relogio_retrato():
    """Ícone do relógio para o retrato do diálogo (48x48)."""
    S = 48
    c = canvas(S, S)
    gold = ramp('6a4410', 'a87420', 'd8a838', 'f8d870', 'fff4c0')
    strap = ramp('2a160c', '4a2a18', '6a4026', '8a5a36')
    face = ramp('0a3040', '146070', '2aa0b0', '73eff7', 'd8ffff')
    for y in range(S):
        for x in range(S):
            if 18 <= x <= 29 and (y < 12 or y > 35):
                v = 0.55 + (0.2 if x in (19, 20) else 0) - (0.25 if x in (28, 29) else 0)
                if y % 5 == 0:
                    v -= 0.2
                shade_px(c, x, y, strap, v)
    for y in range(S):
        for x in range(S):
            d = np.hypot(x + .5 - 24, y + .5 - 24)
            if d <= 14:
                if d > 11.5:
                    shade_px(c, x, y, gold, 0.75 - (x + y - 48) * 0.012)
                else:
                    v = 0.55 + (11.5 - d) * 0.03 + (0.2 if (x - y) in (-6, -5) and d < 9 else 0)
                    shade_px(c, x, y, face, v, dither=0.5)
    # símbolos estranhos no lugar dos números
    simb = hexc('5d275d')
    for k in range(8):
        a = k * np.pi / 4
        sx, sy = 24 + np.cos(a) * 9, 24 + np.sin(a) * 9
        put(c, int(sx), int(sy), simb)
        put(c, int(sx) + (k % 2), int(sy) + ((k + 1) % 2), simb)
    # ponteiros (girando ao contrário)
    for t in np.linspace(0, 7, 14):
        put(c, int(24 - t * 0.55), int(24 - t * 0.8), hexc('1a1c2c'))
    for t in np.linspace(0, 5, 10):
        put(c, int(24 + t * 0.9), int(24 + t * 0.2), hexc('1a1c2c'))
    put(c, 24, 24, hexc('ffcd75'))
    put(c, 34, 23, gold[3]); put(c, 34, 24, gold[2]); put(c, 35, 24, gold[1])  # coroa
    return outline(c, hexc('1a1010'))
