"""Arte pixelada do reino para a abertura: relógio, princesa, dragão, castelo, vila, vulcão..."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'arte'))
from paint import (R, ramp, canvas, put, shade_px, outline, blob, vnoise, fbm, hash2, hexc)  # noqa: E402
import objetos as OBJ  # noqa: E402


def rgba(img):
    return np.asarray(img.convert('RGBA')).astype(float) / 255


def C(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# ================================================================== relógio (tela de abertura)

RUNAS = [  # traços de cada runa numa grade 5x7 (x0,y0,x1,y1)
    [(2, 0, 2, 6), (2, 1, 4, 0), (2, 3, 4, 2)],
    [(1, 0, 1, 6), (1, 0, 4, 2), (4, 2, 1, 4)],
    [(0, 6, 2, 0), (2, 0, 4, 6), (1, 3, 3, 3)],
    [(2, 0, 2, 6), (0, 2, 4, 4), (0, 4, 4, 2)],
    [(0, 0, 4, 6), (4, 0, 0, 6)],
    [(1, 0, 1, 6), (4, 0, 4, 6), (1, 2, 4, 4)],
    [(2, 0, 2, 6), (0, 0, 4, 3), (4, 3, 0, 6)],
    [(0, 1, 2, 0), (2, 0, 4, 1), (2, 0, 2, 6), (0, 6, 4, 6)],
    [(0, 0, 0, 6), (0, 0, 4, 3), (0, 6, 4, 3)],
    [(2, 0, 2, 6), (0, 1, 2, 3), (4, 1, 2, 3)],
    [(0, 3, 2, 0), (2, 0, 4, 3), (4, 3, 2, 6), (2, 6, 0, 3)],
    [(1, 0, 3, 0), (2, 0, 2, 6), (0, 4, 4, 4)],
]


def relogio_base(S=112):
    """Relógio grande sem ponteiros; devolve (imagem, camada das runas)."""
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S // 2
    # pulseira de couro
    strap = [C('2a160c'), C('4a2a18'), C('6a4026'), C('8a5a36')]
    for y in list(range(0, c - 30)) + list(range(c + 30, S)):
        for x in range(c - 18, c + 18):
            k = 2 if x < c + 10 else 1
            if x in (c - 18, c + 17):
                k = 0
            if y % 9 == 0:
                k = max(0, k - 1)
            d.point((x, y), strap[k])
    for y in (8, 18, S - 19, S - 9):  # furinhos
        d.rectangle((c - 2, y, c + 1, y + 2), C('1a0c06'))
    # caixa dourada
    d.ellipse((c - 42, c - 42, c + 41, c + 41), C('5a3a10'))
    d.ellipse((c - 40, c - 40, c + 39, c + 39), C('d8a838'))
    d.ellipse((c - 38, c - 38, c + 37, c + 37), C('f8d870'))
    d.ellipse((c - 35, c - 35, c + 34, c + 34), C('a87420'))
    d.ellipse((c - 33, c - 33, c + 32, c + 32), C('0a2a38'))
    # coroa
    d.rectangle((c + 40, c - 5, c + 47, c + 4), C('d8a838'))
    d.rectangle((c + 42, c - 7, c + 47, c + 6), C('a87420'))
    a = np.asarray(img).astype(float) / 255
    # mostrador: gradiente azul-turquesa com pontilhado
    yy, xx = np.mgrid[0:S, 0:S]
    rr = np.hypot(xx + .5 - c, yy + .5 - c)
    face = rr < 32.5
    face_r = ramp('061c28', '0c3444', '145a6a', '1e8a96', '3ac0c8')
    v = .75 - rr / 40 + (fbm(xx * .15, yy * .15, 3) - .5) * .25
    from paint import BAYER
    n = len(face_r) - 1
    f = np.clip(v, 0, .999) * n
    i = np.floor(f).astype(int)
    i = np.where((f - i > BAYER[yy % 4, xx % 4]) & (i < n), i + 1, i)
    a[face, :3] = face_r[i][face]
    # brilho de vidro
    glass = face & (np.abs((xx - c) + (yy - c) * 1.0 + 16) < 2) & (rr < 28)
    a[glass, :3] = a[glass, :3] * .6 + .4
    # anel de marcas
    for k in range(60):
        ang = k / 60 * 2 * np.pi
        r0 = 29 if k % 5 else 27
        for rr_ in np.linspace(r0, 31, 4):
            x, y = int(c + np.cos(ang) * rr_), int(c + np.sin(ang) * rr_)
            a[y, x, :3] = hexc('73eff7') if k % 5 == 0 else hexc('2a6a78')
    # runas (camada separada para brilhar)
    runas = np.zeros((S, S, 4))
    for k, glifo in enumerate(RUNAS):
        ang = -np.pi / 2 + k / 12 * 2 * np.pi
        cx, cy = c + np.cos(ang) * 21, c + np.sin(ang) * 21
        for (x0, y0, x1, y1) in glifo:
            for t in np.linspace(0, 1, 12):
                x = int(round(cx - 2 + x0 + (x1 - x0) * t))
                y = int(round(cy - 3 + y0 + (y1 - y0) * t))
                runas[y, x] = (1, .95, .7, 1)
                runas[y, x + 1, :] = runas[y, x + 1, :] if runas[y, x + 1, 3] else (0.3, .2, .45, 1)
    return a, runas


def ponteiros(S, ang_h, ang_m, ang_s):
    """Camada com os ponteiros (ângulos em radianos; 0 = 12h, sentido horário)."""
    L = np.zeros((S, S, 4))
    c = S / 2 - .5

    def linha(ang, comp, larg, cor):
        for t in np.linspace(-3, comp, int(comp * 3)):
            x = c + np.sin(ang) * t
            y = c - np.cos(ang) * t
            for w in range(-larg, larg + 1):
                px = int(round(x + np.cos(ang) * w * .7))
                py = int(round(y + np.sin(ang) * w * .7))
                if 0 <= px < S and 0 <= py < S:
                    L[py, px] = cor

    linha(ang_h, 15, 1, (*hexc('1a1c2c'), 1))
    linha(ang_m, 24, 1, (*hexc('1a1c2c'), 1))
    linha(ang_s, 27, 0, (*hexc('ffcd75'), 1))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            L[int(c) + dy, int(c) + dx] = (*hexc('ffcd75'), 1)
    return L


# ================================================================== princesa (24x44)

def princesa(sorrindo=False, brilho_seed=0):
    W, H = 24, 44
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    skin, skin_s = C('f6d2b4'), C('dca688')
    hair, hair_s, hair_h = C('f2c84a'), C('c8962a'), C('fff0a0')
    dress, dress_s, dress_d = C('2a4aa8'), C('1a2c78'), C('101a4a')
    # cabelo de trás (longo)
    d.polygon([(5, 6), (18, 6), (21, 30), (3, 30)], hair_s)
    # vestido (saia em sino)
    d.polygon([(8, 20), (15, 20), (21, 42), (2, 42)], dress)
    d.polygon([(2, 42), (21, 42), (21, 43), (2, 43)], dress_d)
    d.polygon([(13, 21), (15, 20), (21, 42), (16, 42)], dress_s)
    # corpete
    d.rectangle((8, 17, 15, 23), dress)
    d.rectangle((13, 17, 15, 23), dress_s)
    d.line((8, 23, 15, 23), C('ffcd75'))  # cinto dourado
    # braços
    d.rectangle((6, 18, 7, 26), skin)
    d.rectangle((16, 18, 17, 26), skin_s)
    # pescoço e rosto
    d.rectangle((10, 14, 13, 16), skin_s)
    d.ellipse((6, 4, 17, 15), skin)
    # cabelo da frente (franja e laterais)
    d.pieslice((5, 1, 18, 14), 180, 360, hair)
    d.polygon([(5, 7), (8, 7), (7, 18), (4, 22)], hair)
    d.polygon([(15, 7), (18, 7), (19, 22), (16, 18)], hair)
    d.line((8, 3, 12, 2), hair_h)
    d.point((9, 4), hair_h)
    # tiara
    d.line((7, 3, 16, 3), C('ffe27a'))
    d.point((11, 1), C('ffe27a')); d.point((12, 1), C('ffe27a')); d.point((11, 2), C('8af0ff'))
    # olhos verdes
    for ex in (9, 13):
        d.rectangle((ex, 9, ex + 1, 10), C('1e8a4a'))
        d.point((ex, 9), C('ffffff'))
        d.point((ex + 1, 10), C('0a3a1a'))
    d.line((9, 8, 10, 8), C('8a5a2a')); d.line((13, 8, 14, 8), C('8a5a2a'))  # cílios
    # bochechas e boca
    d.point((8, 12), C('f0a090')); d.point((15, 12), C('f0a090'))
    if sorrindo:
        d.line((10, 13, 13, 13), C('c0505a'))
        d.point((9, 12), C('c0505a')); d.point((14, 12), C('c0505a'))
        d.point((11, 13), C('fff6ec'))
    else:
        d.line((11, 13, 12, 13), C('c0606a'))
    a = rgba(img)
    # estrelas no vestido (cintilam: semente muda o padrão)
    rng = np.random.default_rng(brilho_seed)
    for _ in range(14):
        x, y = rng.integers(3, 21), rng.integers(18, 42)
        if a[y, x, 3] > .5 and a[y, x, 2] > .2:
            a[y, x, :3] = (1, 1, .9) if rng.random() < .5 else hexc('aee8ff')
    return outline(a, hexc('1a1030'))


# ================================================================== dragão (48x32, 3 quadros)

def dragao(quadro):
    W, H = 52, 34
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body, body_s, belly = C('c0302a'), C('7a1a1a'), C('f0b040')
    wing, wing_s = C('8a2028'), C('5a1018')
    # asa de trás (posição depende do quadro)
    asa_y = [2, 12, 22][quadro]
    d.polygon([(22, 15), (30, 14), (40, asa_y), (34, asa_y + 2), (28, asa_y + 5)], wing_s)
    # cauda
    d.polygon([(4, 20), (16, 16), (18, 20), (8, 23)], body_s)
    d.polygon([(0, 22), (4, 19), (5, 23)], body)
    # corpo
    d.ellipse((14, 13, 36, 24), body)
    d.ellipse((17, 19, 34, 25), belly)
    # pescoço e cabeça
    d.polygon([(32, 15), (40, 9), (43, 12), (36, 19)], body)
    d.polygon([(40, 7), (49, 9), (50, 12), (42, 14)], body)
    d.polygon([(41, 7), (43, 3), (44, 7)], body_s)  # chifre
    d.point((45, 9), C('ffe27a'))  # olho
    d.line((46, 12, 50, 12), body_s)
    # patas
    d.line((20, 24, 19, 28), body_s); d.line((30, 24, 31, 28), body_s)
    # asa da frente
    d.polygon([(20, 16), (26, 15), (24 + quadro * 2, asa_y - 1), (12, asa_y + 3), (14, asa_y + 8)], wing)
    for k in range(3):  # nervuras
        d.line((22, 16, 12 + k * 5, asa_y + 3 - k), wing_s)
    return outline(rgba(img), hexc('2a0a0a'))


# ================================================================== vila e castelo

def parede_casa(cor, w=48, h=32, seed=0, porta=True):
    """Fachada de casa colorida: reboco, janelas com floreira, porta."""
    rmp = ramp(*cor)
    c = canvas(w, h)
    for y in range(h):
        for x in range(w):
            v = .6 + (fbm(x * .2, y * .2, seed) - .5) * .4 - (y / h) ** 3 * .2
            shade_px(c, x, y, rmp, v)
    for y in range(h - 3, h):  # rodapé de pedra
        for x in range(w):
            shade_px(c, x, y, R['stone'], .5 - (y - h + 3) * .1)
    rng = np.random.default_rng(seed)
    nj = max(1, w // 16)
    for i in range(nj):
        x0 = int((i + .5) * w / nj) - 4
        if porta and i == nj // 2:
            for y in range(h - 15, h - 1):
                for x in range(x0, x0 + 8):
                    edge = x in (x0, x0 + 7) or y == h - 15
                    shade_px(c, x, y, R['wood'], .3 if edge else .55)
            put(c, x0 + 6, h - 8, R['yellow'][2])
            continue
        for y in range(8, 17):
            for x in range(x0, x0 + 8):
                edge = x in (x0, x0 + 7) or y in (8, 16)
                if edge:
                    put(c, x, y, R['white'][2])
                else:
                    shade_px(c, x, y, R['glass'], .85 - (y - 8) * .08)
        for x in range(x0 - 1, x0 + 9):
            shade_px(c, x, 17, R['wood'], .5)
            put(c, x, 16, (R['red'] if rng.random() < .5 else R['pink'])[rng.integers(2, 4)] if x % 2 else R['leaf'][3])
    return c


def telhado_cor(cor, w=48, h=24, seed=0):
    rmp = ramp(*cor)
    c = canvas(w, h)
    for y in range(h):
        row = y // 4
        for x in range(w):
            xx = x + (2 if row % 2 else 0)
            v = .65 - (y % 4) * .1 + (vnoise(x * .3, y * .3, seed) - .5) * .3
            if xx % 6 == 0:
                v -= .3
            if y % 4 == 3:
                v = .1
            shade_px(c, x, y, rmp, v)
    return c


def triangulo_parede(cor, w=48, h=16, seed=0):
    """Empena (triângulo da parede embaixo do telhado), textura retangular — o triângulo é a malha."""
    return parede_casa(cor, w, h, seed, porta=False)


def pedra_castelo(w=64, h=64, seed=0, janelas=True, ameias=False):
    rmp = ramp('3a3a52', '5a5a76', '7a7a96', '9e9cb6', 'c8c4d8')
    c = canvas(w, h)
    for y in range(h):
        for x in range(w):
            row = y // 6
            bx = (x + (5 if row % 2 else 0)) % 10
            v = .55 + (vnoise(x * .4, y * .4, seed) - .5) * .35
            if bx == 0 or y % 6 == 0:
                v = .18
            shade_px(c, x, y, rmp, v)
    if ameias:
        for y in range(0, 6):
            for x in range(w):
                if (x // 5) % 2 == 1:
                    c[y, x, 3] = 0
    if janelas:
        for x0 in range(8, w - 8, 20):
            for y in range(20, 32):
                for x in range(x0, x0 + 5):
                    top = 20 + (1 if x in (x0, x0 + 4) else 0)
                    if y >= top:
                        shade_px(c, x, y, R['glass'], .7 if y < 25 else .45)
    return c


def telhado_torre(cor=('1a1a5a', '2a3a9a', '3a5ad0', '6a8af0', 'a8c0ff'), w=64, h=48):
    rmp = ramp(*cor)
    c = canvas(w, h)
    for y in range(h):
        for x in range(w):
            v = .55 - (y % 5) * .07 + (0.25 if (x // 4) % 2 else 0) * (1 - y / h) * .4
            if y % 5 == 4:
                v = .12
            shade_px(c, x, y, rmp, v)
    return c


def bandeira(quadro):
    W, H = 14, 18
    c = canvas(W, H)
    for y in range(H):
        put(c, 1, y, R['wood'][1])
    for y in range(1, 9):
        for x in range(2, 13):
            wav = int(np.round(np.sin(x * .6 + quadro * 1.6)))
            yy = y + wav
            if 0 <= yy < H:
                put(c, x, yy, hexc('e04848') if y < 5 else hexc('f0c040'))
    return outline(c)


# ================================================================== natureza

def pinheiro(s=0):
    W, H = 28, 52
    c = canvas(W, H)
    rmp = ramp('0a201c', '12342a', '1c4a34', '2c6440', '4a8450')
    for layer in range(5):
        top = 2 + layer * 8
        bot = top + 16
        for y in range(top, min(bot, H - 6)):
            half = (y - top) * .62 + 1 + layer * .8
            for x in range(int(14 - half), int(14 + half) + 1):
                v = .55 - (x - 14) / max(half, 1) * .25 - (y - top) / 20 + (vnoise(x * .5, y * .5, s) - .5) * .3
                shade_px(c, x, y, rmp, v)
    for y in range(H - 8, H):
        for x in (13, 14):
            shade_px(c, x, y, R['bark'], .5 if x == 13 else .3)
    for y in range(2, 8):  # neve
        for x in range(10, 18):
            if c[y, x, 3] > 0 and (x + y) % 3:
                put(c, x, y, R['white'][2])
    return outline(c, hexc('06120e'))


def nuvem(s=0):
    W, H = 96, 40
    c = canvas(W, H)
    rng = np.random.default_rng(s)
    yy, xx = np.mgrid[0:H, 0:W]
    a = np.zeros((H, W))
    for _ in range(7):
        cx, cy, r = rng.uniform(18, W - 18), rng.uniform(16, 26), rng.uniform(9, 17)
        a = np.maximum(a, np.clip(1 - np.hypot((xx - cx) / r, (yy - cy) / (r * .75)), 0, 1))
    a = np.clip(a * 2.2, 0, 1)
    shade = np.clip(.95 - (yy / H) * .35, 0, 1)
    c[..., 0] = shade * 1.0; c[..., 1] = shade * .97; c[..., 2] = shade * .95
    c[..., 3] = (a > .35).astype(float)
    # borda de baixo levemente rosada (luz da tarde)
    m = (yy > H * .55) & (c[..., 3] > 0)
    c[m, :3] = c[m, :3] * np.array([1, .88, .85])
    return c


def guarda_sol(cor):
    W, H = 18, 22
    c = canvas(W, H)
    for y in range(8, H):
        put(c, 9, y, R['white'][1])
    for y in range(0, 8):
        half = 1 + y * 1.1
        for x in range(int(9 - half), int(9 + half) + 1):
            stripe = ((x - 9) // 3) % 2
            put(c, x, y, hexc(cor) if stripe else hexc('fff4e0'))
    return outline(c)


def banhista(tipo, seed=0):
    """Pessoinhas da praia (vistas de longe)."""
    W, H = 10, 16
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    pele = [C('f2c9a6'), C('c48e6c'), C('8a5a3c')][rng.integers(0, 3)]
    roupa = [C('e04848'), C('3a8ae0'), C('f0c040'), C('40b070'), C('e070b0')][rng.integers(0, 5)]
    cabelo = [C('2a1810'), C('f2c84a'), C('6a3a20')][rng.integers(0, 3)]
    if tipo == 'deitado':
        img = Image.new('RGBA', (16, 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 5, 15, 7), [C('f0f0f0'), C('e04848'), C('3ac0c8')][rng.integers(0, 3)])  # toalha
        d.rectangle((3, 3, 12, 5), pele)
        d.rectangle((6, 3, 9, 5), roupa)
        d.ellipse((12, 2, 15, 5), pele)
        d.point((14, 2), cabelo)
    else:
        d.ellipse((3, 0, 7, 4), pele)
        d.line((3, 0, 7, 0), cabelo)
        d.rectangle((3, 5, 6, 10), pele)
        d.rectangle((3, 7, 6, 9), roupa)
        d.line((4, 11, 4, 15), pele); d.line((6, 11, 6, 15), pele)
        if tipo == 'acenando':
            d.line((7, 5, 9, 2), pele)
        else:
            d.line((2, 5, 2, 9), pele); d.line((7, 5, 7, 9), pele)
    return outline(rgba(img), hexc('1a1c2c'))


def barco():
    W, H = 22, 22
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 16), (20, 16), (17, 20), (5, 20)], C('8a5a32'))
    d.line((11, 2, 11, 16), C('4a2c1a'))
    d.polygon([(12, 3), (19, 14), (12, 14)], C('fff4e0'))
    d.polygon([(10, 5), (4, 14), (10, 14)], C('e8e0d0'))
    return outline(rgba(img), hexc('1a1c2c'))


def faisca(cor=('ffffff', 'ffe27a', 'ff8a30')):
    S = 8
    c = canvas(S, S)
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.hypot(xx + .5 - S / 2, yy + .5 - S / 2) / (S / 2)
    c[..., :3] = np.where((d < .4)[..., None], hexc(cor[0]), np.where((d < .7)[..., None], hexc(cor[1]), hexc(cor[2])))
    c[..., 3] = (d < 1).astype(float) * np.clip(1.2 - d, 0, 1)
    return c


def fumaca(s=0):
    S = 32
    c = canvas(S, S)
    yy, xx = np.mgrid[0:S, 0:S]
    n = fbm(xx * .2, yy * .2, s)
    d = np.hypot(xx + .5 - S / 2, yy + .5 - S / 2) / (S / 2)
    a = (d + (n - .5) * .6) < .8
    v = .25 + (n - .5) * .3 - (yy / S) * .1
    c[..., 0] = v; c[..., 1] = v * .95; c[..., 2] = v * .95
    c[..., 3] = a.astype(float)
    return c


def textura_vulcao(W=256, H=128):
    """u = volta em torno do cone, v = de cima (0) para baixo (1). Rocha escura com rios de lava."""
    c = canvas(W, H)
    rocha = ramp('140c0c', '2a1a18', '3e2a24', '5a4034', '7a5a48')
    lava = ramp('6a1008', 'c03010', 'f06a18', 'ffb030', 'fff0a0')
    yy, xx = np.mgrid[0:H, 0:W]
    n = fbm(xx * .06, yy * .08, 77)
    v = .45 + (n - .5) * .8 - (yy / H) * .1
    from paint import BAYER
    def q(rmp, val):
        nn = len(rmp) - 1
        f = np.clip(val, 0, .999) * nn
        i = np.floor(f).astype(int)
        i = np.where((f - i > BAYER[yy % 4, xx % 4]) & (i < nn), i + 1, i)
        return rmp[i]
    col = q(rocha, v)
    # rios de lava descendo
    lava_m = np.zeros((H, W), bool)
    for k in range(6):
        x0 = (k + .3) * W / 6
        path = x0 + np.cumsum(np.sin(np.arange(H) * .15 + k) * .9)
        width = 1.5 + (1 - np.arange(H) / H) * 2.5
        reach = H * (0.45 + 0.5 * hash2(k, 3, 1))
        for y in range(int(reach)):
            dx = np.abs(xx[y] - path[y])
            lava_m[y] |= dx < width[y]
    lv = np.clip(1 - yy / H * .9 + (n - .5) * .4, 0, 1)
    col = np.where(lava_m[..., None], q(lava, .45 + lv * .5), col)
    c[..., :3] = col
    c[..., 3] = 1
    return c, lava_m


def textura_montanha(W=128, H=96, seed=0):
    c = canvas(W, H)
    rocha = ramp('2a2e44', '3e4460', '565e7c', '737c98', '98a0b8')
    yy, xx = np.mgrid[0:H, 0:W]
    n = fbm(xx * .08, yy * .08, seed)
    v = .5 + (n - .5) * .7 + (np.sin(xx * .2 + n * 4) * .08)
    from paint import BAYER
    nn = len(rocha) - 1
    f = np.clip(v, 0, .999) * nn
    i = np.floor(f).astype(int)
    i = np.where((f - i > BAYER[yy % 4, xx % 4]) & (i < nn), i + 1, i)
    col = rocha[i]
    neve = yy < (H * .3 + (n - .5) * 18)
    col = np.where(neve[..., None], np.where(((xx + yy) % 3 == 0)[..., None], hexc('c8d4ec'), hexc('f4f8ff')), col)
    c[..., :3] = col
    c[..., 3] = 1
    return c


def brilho_runa():
    S = 16
    c = canvas(S, S)
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.hypot(xx + .5 - S / 2, yy + .5 - S / 2) / (S / 2)
    c[..., :3] = 1
    c[..., 3] = np.clip(1 - d, 0, 1) ** 2
    return c


def arvores():
    return [OBJ.arvore(s=3 + i * 7) for i in range(4)]


def arvores_mata():
    return [OBJ.arvore_mata(s=40 + i * 5) for i in range(4)]


# ================================================================== vida no reino

def passaro(quadro, gaivota=False):
    """Passarinho visto de longe (asa pra cima / pra baixo)."""
    W, H = 11, 7
    c = canvas(W, H)
    cor = hexc('f4f4f4') if gaivota else hexc('2a2030')
    ponta = hexc('3a3a44') if gaivota else hexc('1a1420')
    if quadro == 0:  # asas para cima (V)
        pts = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 4), (5, 5), (6, 4), (7, 4), (8, 3), (9, 2), (10, 1)]
    else:  # asas para baixo
        pts = [(0, 5), (1, 4), (2, 4), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 4), (9, 4), (10, 5)]
    for (x, y) in pts:
        put(c, x, y, ponta if x in (0, 10) else cor)
    put(c, 5, pts[5][1] + 1, cor)
    return c


def crocodilo(quadro):
    """Crocodilo andando em pé (vista de lado, virado para a direita). 3 quadros de passo."""
    W, H = 34, 44
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pele, sombra, barriga, escuro = C('4a8a3a'), C('2e5e28'), C('d8d088'), C('1e3a1a')
    # cauda
    d.polygon([(10, 26), (2, 36), (0, 42), (6, 40), (13, 32)], sombra)
    # perna de trás e da frente (alternam)
    passo = [(-3, 3), (0, 0), (3, -3)][quadro]
    d.polygon([(12, 30), (16, 30), (16 + passo[0], 41), (11 + passo[0], 41)], sombra)
    d.polygon([(17, 30), (21, 30), (21 + passo[1], 41), (16 + passo[1], 41)], pele)
    d.rectangle((10 + passo[0], 41, 17 + passo[0], 43), escuro)
    d.rectangle((15 + passo[1], 41, 23 + passo[1], 43), escuro)
    # corpo
    d.ellipse((9, 13, 24, 33), pele)
    d.ellipse((15, 16, 24, 31), barriga)
    for y in range(18, 31, 3):
        d.line((16, y, 23, y), C('b8b070'))
    # colete vermelho (dá um ar de personagem de fábula)
    d.polygon([(10, 16), (16, 15), (15, 27), (10, 28)], C('a8303a'))
    # braço balançando
    d.line((18, 19, 23 + passo[0] // -1, 26), sombra, width=3)
    # cabeça com focinho comprido
    d.ellipse((11, 4, 22, 15), pele)
    d.polygon([(18, 6), (33, 9), (33, 13), (19, 14)], pele)
    d.line((19, 12, 32, 12), escuro)
    for x in range(21, 32, 3):
        d.point((x, 11), C('ffffff'))  # dentinhos
    d.ellipse((15, 5, 19, 9), C('f0e060'))
    d.point((17, 7), C('101010'))
    d.point((32, 9), escuro)
    # escamas nas costas
    for y in range(14, 30, 4):
        d.polygon([(10, y), (8, y + 2), (10, y + 3)], sombra)
    return outline(rgba(img), hexc('10200c'))


def carroca(quadro):
    """Cavalo puxando carroça (vista de lado, virado para a direita)."""
    W, H = 48, 26
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    madeira, madeira_s = C('8a5a32'), C('5a3a1e')
    cavalo, cavalo_s, crina = C('a86a3a'), C('7a4a26'), C('3a2216')
    # carroça
    d.rectangle((1, 9, 22, 17), madeira)
    d.rectangle((1, 15, 22, 17), madeira_s)
    for x in (5, 11, 17):
        d.line((x, 9, x, 17), madeira_s)
    d.ellipse((2, 4, 12, 11), C('e8d098'))  # carga (sacos de trigo)
    d.ellipse((9, 3, 20, 11), C('c04040'))  # maçãs
    d.ellipse((5, 14, 15, 24), C('3a2a1a'))
    d.ellipse((7, 16, 13, 22), madeira)
    d.point((10, 19), C('3a2a1a'))
    rot = quadro * 2
    d.line((10 - rot, 16, 10 + rot, 22), C('3a2a1a'))
    d.line((22, 13, 30, 13), madeira_s)  # varal
    # cavalo
    d.ellipse((26, 7, 42, 17), cavalo)
    d.polygon([(38, 9), (43, 2), (47, 5), (44, 11)], cavalo)
    d.polygon([(43, 2), (47, 4), (47, 7), (45, 6)], cavalo_s)
    d.line((38, 6, 42, 2), crina, width=2)
    d.point((44, 4), C('101010'))
    pernas = [((28, 17, 27, 25), (39, 17, 41, 25)), ((28, 17, 30, 25), (39, 17, 37, 25))][quadro]
    for (x0, y0, x1, y1) in pernas:
        d.line((x0, y0, x1, y1), cavalo_s, width=2)
    d.line((26, 10, 23, 15), crina, width=2)  # rabo
    # cocheiro
    d.ellipse((14, 0, 19, 5), C('f2c9a6'))
    d.rectangle((14, 5, 19, 10), C('3a6ad0'))
    d.line((13, 0, 20, 0), C('8a5a32'))
    return outline(rgba(img), hexc('1a1008'))


def aldeao(seed, quadro=0):
    """Morador da vila (túnica/vestido colorido), 2 quadros de passo."""
    W, H = 10, 18
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    pele = [C('f2c9a6'), C('d8a080'), C('a06a48'), C('6a4028')][rng.integers(0, 4)]
    roupa = [C('c04040'), C('3a6ad0'), C('40a060'), C('e0a030'), C('9a4ab0'), C('e070a0')][rng.integers(0, 6)]
    cabelo = [C('2a1810'), C('f2c84a'), C('6a3a20'), C('a0a0a0')][rng.integers(0, 4)]
    vestido = rng.random() < .5
    d.ellipse((3, 0, 7, 4), pele)
    d.line((3, 0, 7, 0), cabelo); d.point((3, 1), cabelo); d.point((7, 1), cabelo)
    if vestido:
        d.polygon([(4, 5), (6, 5), (8, 14), (2, 14)], roupa)
    else:
        d.rectangle((3, 5, 7, 11), roupa)
        d.rectangle((3, 11, 7, 13), C('5a4030'))
    d.line((2, 6, 2 - quadro, 10), pele); d.line((8, 6, 8 + quadro, 10), pele)
    if quadro == 0:
        d.line((4, 14, 4, 17), C('3a2a1a')); d.line((6, 14, 6, 17), C('3a2a1a'))
    else:
        d.line((4, 14, 3, 17), C('3a2a1a')); d.line((6, 14, 7, 17), C('3a2a1a'))
    if rng.random() < .3:  # cesta
        d.rectangle((7, 8, 9, 10), C('c8a060'))
    return outline(rgba(img), hexc('1a1c2c'))


def barraca(cor, seed=0):
    """Barraca de feira com toldo listrado e mercadorias."""
    W, H = 34, 30
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    madeira, madeira_s = C('8a5a32'), C('5a3a1e')
    # estacas
    d.rectangle((2, 8, 3, 29), madeira_s); d.rectangle((30, 8, 31, 29), madeira_s)
    # balcão
    d.rectangle((1, 19, 32, 28), madeira)
    d.rectangle((1, 26, 32, 28), madeira_s)
    for x in range(4, 32, 6):
        d.line((x, 19, x, 28), madeira_s)
    # mercadorias no balcão
    mercadorias = [C('d04040'), C('f0c040'), C('60b040'), C('f08a30'), C('9a4ab0'), C('e8e0c0')]
    for x in range(3, 31, 4):
        cor_m = mercadorias[rng.integers(0, len(mercadorias))]
        d.ellipse((x, 15, x + 3, 19), cor_m)
        d.ellipse((x + 1, 13, x + 4, 17), cor_m)
    # toldo listrado com babado
    for i in range(0, 34, 4):
        d.polygon([(i, 2), (i + 4, 2), (i + 4, 9), (i, 9)], C(cor) if (i // 4) % 2 == 0 else C('fff4e0'))
    for i in range(0, 34, 4):
        d.pieslice((i, 6, i + 4, 12), 0, 180, C(cor) if (i // 4) % 2 == 0 else C('fff4e0'))
    d.line((0, 1, 33, 1), madeira_s)
    return outline(rgba(img), hexc('1a1008'))


# ================================================================== porto

def navio(seed=0):
    """Veleiro grande (galeão) visto de lado, virado para a direita."""
    W, H = 80, 72
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    casco, casco_s, casco_c = C('6a3a1e'), C('3e2010'), C('9a6a3a')
    vela, vela_s = C('f4ecd8'), C('d0c4a8')
    faixa = [C('c04040'), C('2a5ab0'), C('d0a030')][seed % 3]
    # casco
    d.polygon([(4, 50), (76, 46), (70, 62), (12, 64)], casco)
    d.polygon([(4, 50), (76, 46), (75, 50), (5, 54)], casco_c)
    d.line((8, 56, 72, 54), faixa, width=2)
    d.polygon([(60, 38), (76, 36), (76, 46), (58, 47)], casco)  # castelo de popa
    d.polygon([(4, 44), (16, 44), (16, 50), (4, 50)], casco)
    for x in range(14, 66, 7):
        d.rectangle((x, 57, x + 2, 59), casco_s)  # escotilhas
    d.polygon([(12, 64), (70, 62), (68, 64), (14, 66)], casco_s)
    # mastros
    for mx, top in ((24, 4), (44, 1), (64, 12)):
        d.line((mx, top, mx, 50), C('4a2a14'), width=2)
    # velas infladas
    for (mx, top, w, h) in ((24, 8, 13, 15), (24, 25, 15, 16), (44, 5, 15, 16), (44, 23, 17, 18), (64, 16, 10, 14)):
        d.polygon([(mx - w, top), (mx + w, top), (mx + w - 2, top + h), (mx - w + 2, top + h)], vela)
        d.line((mx - w + 2, top + h, mx + w - 2, top + h), vela_s)
        d.line((mx - w, top + 3, mx + w, top + 3), vela_s)
    d.polygon([(4, 44), (0, 30), (20, 42)], vela)  # bujarrona
    # bandeiras
    d.polygon([(44, 1), (52, 3), (44, 5)], faixa)
    d.polygon([(24, 4), (30, 6), (24, 8)], faixa)
    return outline(rgba(img), hexc('1a0c04'))


def marinheiro(carregando, quadro):
    W, H = 12, 18
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pele = C('d8a080')
    d.ellipse((4, 2, 8, 6), pele)
    d.line((4, 2, 8, 2), C('2a3a8a'))  # gorro
    d.point((6, 1), C('2a3a8a'))
    for y in range(7, 12):  # camisa listrada
        d.line((4, y, 8, y), C('ffffff') if y % 2 else C('2a5ab0'))
    d.rectangle((4, 12, 8, 13), C('2a2a44'))
    if quadro == 0:
        d.line((5, 14, 5, 17), C('2a2a44')); d.line((7, 14, 7, 17), C('2a2a44'))
    else:
        d.line((5, 14, 4, 17), C('2a2a44')); d.line((7, 14, 8, 17), C('2a2a44'))
    if carregando:
        d.rectangle((2, 0, 10, 4), C('b88a50'))  # caixote no ombro
        d.line((2, 2, 10, 2), C('7a5a30'))
        d.rectangle((2, 0, 10, 4), outline=C('5a3a1e'))
        d.line((3, 7, 3, 4), pele); d.line((9, 7, 9, 4), pele)
    else:
        d.line((3, 7, 3, 11), pele); d.line((9, 7, 9, 11), pele)
    return outline(rgba(img), hexc('1a1c2c'))


def caixotes(seed=0):
    W, H = 20, 16
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for (x, y) in ((0, 8), (9, 8), (4, 0)):
        if rng.random() < .85:
            d.rectangle((x, y, x + 9, y + 7), C('b88a50'))
            d.rectangle((x, y, x + 9, y + 7), outline=C('5a3a1e'))
            d.line((x, y, x + 9, y + 7), C('8a6a38'))
    d.ellipse((14, 4, 19, 15), C('8a5a32'))  # barril
    d.line((14, 8, 19, 8), C('4a2c14')); d.line((14, 12, 19, 12), C('4a2c14'))
    return outline(rgba(img), hexc('1a1008'))


def tabuas(w=32, h=32, seed=0):
    c = canvas(w, h)
    for y in range(h):
        for x in range(w):
            v = .55 + (vnoise(x * .4, y * .08, seed) - .5) * .35
            if x % 6 == 0:
                v = .2
            if (y + (x // 6) * 7) % 23 == 0:
                v = .3
            shade_px(c, x, y, R['wood'], v + .1)
    return c
