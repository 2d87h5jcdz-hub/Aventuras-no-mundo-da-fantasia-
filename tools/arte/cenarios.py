"""Texturas dos cenários, geradas a partir dos mapas em Assets/Scripts/World/Maps.cs."""
import re
import numpy as np
from paint import R, BAYER, ramp, canvas, put, shade_px, vnoise, fbm, hash2, hexc
import objetos as O

PPU = 16
MARGEM = 8  # tiles extras em volta de cada mapa (tem que bater com SceneBuilder.Margin no C#)


def ler_mapas(maps_cs):
    src = open(maps_cs, encoding='utf-8').read()
    return {n: re.findall(r'"(.*?)"', b)
            for n, b in re.findall(r'MapDef\("(\w+)", new\[\]\s*\{(.*?)\}\);', src, re.S)}


def quant(rmp, v, xs, ys, dither=1.0):
    n = len(rmp) - 1
    f = np.clip(v, 0, 0.9999) * n
    i = np.floor(f).astype(int)
    thr = 0.5 + (BAYER[ys % 4, xs % 4] - 0.5) * dither
    i = np.where((f - i > thr) & (i < n), i + 1, i)
    return rmp[i]


# ------------------------------------------------------------------ chão

CLASSE = {
    'Escola': {':': 'terra', 'X': 'terra', ',': 'flores'},
    'Casa': {'r': 'tapete'},
    'Quarto': {'r': 'tapete'},
    'Floresta': {';': 'capim', '!': 'clareira'},
}
PADRAO = {'Escola': 'grama', 'Casa': 'piso', 'Quarto': 'piso', 'Floresta': 'mata'}
FORA = {'Escola': 'grama', 'Casa': 'vazio', 'Quarto': 'vazio', 'Floresta': 'mata'}
FLORESTA = ramp('0e2420', '163a30', '1f5038', '2c6a40', '42884a', '6aa858')


def classe_tile(nome, rows, tx, ty):
    """Classe do chão no tile (tx, ty) do mapa com margem."""
    W, H = len(rows[0]), len(rows)
    x, y = tx - MARGEM, ty - MARGEM
    if 0 <= x < W and 0 <= y < H:
        return CLASSE[nome].get(rows[y][x], PADRAO[nome])
    if nome == 'Escola' and y >= H:
        # o caminho de terra continua depois da saída
        if any(rows[H - 1][xx] == 'X' and abs(xx - x) <= 0 for xx in range(W)):
            return 'terra'
    return FORA[nome]


def chao(nome, rows):
    W, H = len(rows[0]) + 2 * MARGEM, len(rows) + 2 * MARGEM
    w, h = W * PPU, H * PPU
    ys, xs = np.mgrid[0:h, 0:w]
    # borda irregular entre classes: desloca o ponto consultado com ruído
    jx = (vnoise(xs * .18, ys * .18, 41) - .5) * 9
    jy = (vnoise(xs * .18, ys * .18, 42) - .5) * 9
    tx = np.clip(((xs + jx) // PPU).astype(int), 0, W - 1)
    ty = np.clip(((ys + jy) // PPU).astype(int), 0, H - 1)
    lut = {}
    cls = np.empty((H, W), dtype=object)
    for yy in range(H):
        for xx in range(W):
            cls[yy, xx] = classe_tile(nome, rows, xx, yy)
    # interiores: sem borda irregular (piso/tapete têm linhas retas)
    if nome in ('Casa', 'Quarto'):
        tx, ty = xs // PPU, ys // PPU
    C = cls[ty, tx]
    out = np.zeros((h, w, 3))
    n = fbm(xs * .07, ys * .07, 1)

    def pinta(mask, cor):
        out[mask] = cor[mask]

    # grama
    blade = vnoise(xs * .9, ys * .25, 7)
    vg = .40 + (n - .5) * .8 + np.where(blade > .72, .28, np.where(blade < .22, -.18, 0))
    pinta((C == 'grama') | (C == 'flores'), quant(R['grass'], vg, xs, ys))
    # terra
    vd = .5 + (n - .5) * .7 + (vnoise(xs * .6, ys * .6, 9) - .5) * .35
    pinta(C == 'terra', quant(R['dirt'], vd, xs, ys))
    pedra = (C == 'terra') & (hash2(xs, ys, 4) > .985)
    out[pedra] = R['stone'][3]
    # chão da mata
    vm = .38 + (n - .5) * .9 + np.where(blade > .78, .25, 0) + (vnoise(xs * .35, ys * .35, 17) - .5) * .3
    pinta(C == 'mata', quant(FLORESTA, vm, xs, ys))
    vc = vm + .12 + np.where(vnoise(xs * 1.1, ys * .2, 19) > .6, .25, 0)
    pinta(C == 'capim', quant(FLORESTA, vc, xs, ys))
    pinta(C == 'clareira', quant(FLORESTA, vm + .25, xs, ys))
    folhas = (C == 'mata') & (hash2(xs, ys, 23) > .992)
    out[folhas] = R['dirt'][3]
    # piso de madeira (tábuas horizontais de 4 px com emendas)
    row = ys // 4
    junta = ((xs + (row * 37) % 48) % 48) == 0
    vp = .55 + (vnoise(xs * .05, row * 3.1, 13) - .5) * .4 + (vnoise(xs * .6, ys * .9, 14) - .5) * .12
    vp = np.where((ys % 4 == 3) | junta, .18, vp)
    pinta(C == 'piso', quant(R['wood'], vp + .1, xs, ys, dither=.4))
    # tapete: borda dourada + losangos (relativo ao retângulo do tapete)
    if (cls == 'tapete').any():
        tys, txs = np.where(cls == 'tapete')
        x0, x1 = txs.min() * PPU, (txs.max() + 1) * PPU
        y0, y1 = tys.min() * PPU, (tys.max() + 1) * PPU
        rx, ry = xs - x0, ys - y0
        dmin = np.minimum.reduce([rx, ry, x1 - 1 - xs, y1 - 1 - ys])
        TAP = ramp('3a0c18', '6a1828', '9a2a3a', 'c04a4a', 'e07a5a')
        lozango = (np.abs(((rx - (x1 - x0) / 2) % 12) - 6) + np.abs(((ry - (y1 - y0) / 2) % 12) - 6)) < 3
        vt = np.where(dmin < 2, .9, np.where(dmin < 4, .2, np.where(lozango, .75, .45)))
        franja = dmin == 0
        cor_t = quant(TAP, vt, xs, ys, dither=.3)
        cor_t = np.where(((dmin < 2) & ~franja)[..., None], R['yellow'][1], cor_t)
        pinta(C == 'tapete', cor_t)
    out[C == 'vazio'] = 0
    # flores
    tex = np.concatenate([out, np.ones((h, w, 1))], axis=2)
    rng = np.random.default_rng(3)
    dens = {'grama': 1200, 'flores': 220}
    for yy in range(H):
        for xx in range(W):
            k = cls[yy, xx]
            if k not in dens:
                continue
            for _ in range(rng.poisson(PPU * PPU / dens[k])):
                fx, fy = xx * PPU + rng.integers(2, 14), yy * PPU + rng.integers(2, 14)
                cr = R[rng.choice(['white', 'yellow', 'pink', 'white', 'red'])]
                for _ in range(rng.integers(2, 5)):
                    px, py = fx + rng.integers(-3, 4), fy + rng.integers(-2, 3)
                    if 1 <= px < w - 1 and 1 <= py < h - 1:
                        tex[py, px, :3] = cr[2]
                        tex[py, px - 1, :3] = cr[1]
                        tex[py - 1, px, :3] = cr[3]
                        tex[py + 1, px, :3] = R['grass'][1]
    return tex


# ------------------------------------------------------------------ escola

def fachada_escola(linha):
    """Fachada a partir da linha do mapa com W/w/D (colunas 1..n-2)."""
    cols = linha[1:-1]
    wid, hgt = len(cols) * PPU, int(4.5 * PPU)
    c = canvas(wid, hgt)
    ys, xs = np.mgrid[0:hgt, 0:wid]
    v = .58 + (fbm(xs * .12, ys * .12, 21) - .5) * .45 - .25 * (ys / hgt) ** 3
    c[:, :, :3] = quant(R['plaster'], v, xs, ys)
    c[:, :, 3] = 1
    sv = .5 + (vnoise(xs * .5, ys * .5, 2) - .5) * .5
    bx = (xs + np.where((ys // 4) % 2 == 1, 4, 0)) % 10
    sv = np.where((bx == 0) | (ys % 4 == 0), .12, sv)
    m = ys >= hgt - 9
    c[m, :3] = quant(R['stone'], sv, xs, ys)[m]
    for y in (2, 3, 4):
        c[y, :, :3] = R['wood'][3 if y == 2 else 2]
    for i, ch in enumerate(cols):
        if ch == 'W' and i % 3 == 0:
            x0 = i * PPU + 6
            for dx, k in zip(range(3), (3, 2, 1)):
                c[4:hgt - 9, x0 + dx, :3] = R['wood'][k]
    for i, ch in enumerate(cols):
        if ch == 'w':
            O_window(c, i * PPU + 8 - 11, 14, 22, 26)
    portas = [i for i, ch in enumerate(cols) if ch == 'D']
    if portas:
        cx = (portas[0] + portas[-1] + 1) * PPU // 2
        O_door(c, cx - 18, hgt - 9 - 52, 36, 52)
    return c


def O_window(c, x0, y0, w, h):
    for y in range(y0 - 2, y0 + h + 2):
        for x in range(x0 - 2, x0 + w + 2):
            shade_px(c, x, y, R['wood'], 0.35 if (y < y0 or x < x0) else 0.6)
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            v = 0.95 - (y - y0) / h * 0.75
            if 0 <= (x - x0) - (y - y0) * 0.6 < 3 or 0 <= (x - x0) - (y - y0) * 0.6 - 8 < 1:
                v += 0.3
            shade_px(c, x, y, R['glass'], v)
    for y in range(y0, y0 + h):
        put(c, x0 + w // 2, y, R['wood'][2])
    for x in range(x0, x0 + w):
        put(c, x, y0 + h // 2, R['wood'][2])
    shutter = ramp('2a3a4a', '3a5a6a', '4a7a82', '6aa09a')
    for side in (x0 - 9, x0 + w + 2):
        for y in range(y0 - 2, y0 + h + 2):
            for x in range(side, side + 7):
                v = 0.55 if (y - y0) % 3 else 0.25
                shade_px(c, x, y, shutter, v + (0.2 if x == side + 6 else 0))
    by = y0 + h + 2
    for y in range(by, by + 5):
        for x in range(x0 - 3, x0 + w + 3):
            shade_px(c, x, y, R['wood'], 0.55 if y == by else 0.3)
    rng = np.random.default_rng(x0)
    for i in range(x0 - 2, x0 + w + 2, 2):
        col = R['red'] if rng.random() < 0.6 else R['pink']
        put(c, i, by - 1 - rng.integers(0, 2), col[2])
        put(c, i + 1, by - 1, R['leaf'][3])
        put(c, i, by - 3 + rng.integers(0, 2), col[3])


def O_door(c, x0, y0, w, h):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            dx = (x - x0 - w / 2) / (w / 2)
            top = y0 + 8 - int(8 * np.sqrt(max(0, 1 - dx * dx)))
            if y < top:
                continue
            if y < top + 2 or x in (x0, x0 + w - 1):
                shade_px(c, x, y, R['stone'], 0.75)
                continue
            plank = (x - x0) % 6
            v = 0.5 + (vnoise(x * 0.3, y * 0.08, 6) - 0.5) * 0.5 - (0.3 if plank == 0 else 0)
            if x == x0 + w // 2:
                v = 0.05
            shade_px(c, x, y, R['wood'], v)
    for x in (x0 + w // 2 - 3, x0 + w // 2 + 2):
        put(c, x, y0 + h // 2 + 4, R['yellow'][2])
        put(c, x, y0 + h // 2 + 5, R['yellow'][1])
    for y in range(y0 - 7, y0 - 1):
        for x in range(x0 + 8, x0 + w - 8):
            shade_px(c, x, y, R['wood'], 0.75 if y == y0 - 7 else 0.5)
    for i, x in enumerate(range(x0 + 11, x0 + w - 11, 2)):
        put(c, x, y0 - 4, R['yellow'][3 if i % 2 else 2])


def telhado(largura_u, prof_px=52):
    W = largura_u * PPU
    c = canvas(W, prof_px)
    ys, xs = np.mgrid[0:prof_px, 0:W]
    row = ys // 5
    xx = xs + np.where(row % 2 == 1, 3, 0)
    tx, ty = xx % 7, ys % 5
    v = .62 - ty * .08 + (vnoise(xs * .2, ys * .2, 11) - .5) * .35
    v = np.where(tx == 0, v - .35, v)
    v = np.where(ty == 4, .12, v)
    v = np.where(hash2(xx // 7, row, 3) > .9, v - .15, v)
    v += .15 * (1 - ys / prof_px)
    c[:, :, :3] = quant(R['roof'], v, xs, ys)
    c[:, :, 3] = 1
    return c[::-1].copy()  # linha 0 = cumeeira


def ceu(topo, meio, horizonte, h=128):
    c = canvas(4, h)
    for y in range(h):
        t = 1 - y / (h - 1)  # 1 = topo
        if t < .35:
            col = hexc(horizonte) + (hexc(meio) - hexc(horizonte)) * (t / .35)
        else:
            col = hexc(meio) + (hexc(topo) - hexc(meio)) * ((t - .35) / .65)
        c[y, :, :3] = col
        c[y, :, 3] = 1
    return c


# ------------------------------------------------------------------ interiores

WALLPAPER = ramp('5a6a86', '7a8aa6', '94a6be', 'b4c4d6', 'd4e0ea')
ALTURA_PAREDE = 3.0


def parede(linha, porta_aberta_ok=True):
    """Parede do fundo a partir da linha 0 do mapa (#, n janela, k estante, d porta)."""
    wid, hgt = len(linha) * PPU, int(ALTURA_PAREDE * PPU)
    c = canvas(wid, hgt)
    ys, xs = np.mgrid[0:hgt, 0:wid]
    stripe = (xs % 8 < 1)
    flor = ((xs + (ys // 8) * 4) % 8 == 4) & (ys % 8 == 3)
    v = .5 + (fbm(xs * .1, ys * .1, 5) - .5) * .2 - np.where(stripe, .12, 0) + np.where(flor, .18, 0)
    v -= .25 * (1 - ys / hgt) ** 4  # sombra perto do teto
    c[:, :, :3] = quant(WALLPAPER, v, xs, ys, dither=.5)
    c[:, :, 3] = 1
    # rodapé/lambri de madeira
    base = hgt - 14
    for y in range(base, hgt):
        for x in range(wid):
            vv = .55 if y > base + 1 else .8
            if (x % 12) == 0 and y > base + 1:
                vv = .3
            if y == hgt - 1:
                vv = .2
            shade_px(c, x, y, R['wood'], vv)
    for x in range(wid):  # moldura do teto
        shade_px(c, x, 0, R['wood'], .3)
        shade_px(c, x, 1, R['wood'], .6)
    for i, ch in enumerate(linha):
        x0 = i * PPU
        if ch == 'n':
            janela_noite(c, x0 + 2, 8, 12, 16)
        elif ch == 'k':
            estante(c, x0, 6, 16, hgt - 6)
        elif ch == 'd':
            for y in range(6, hgt):
                for x in range(x0 + 1, x0 + 15):
                    put(c, x, y, hexc('0a0808'))  # vão escuro atrás da porta
    return c


def janela_noite(c, x0, y0, w, h):
    NOITE = ramp('080c24', '101a40', '1a2a5a', '2a4078')
    for y in range(y0 - 1, y0 + h + 1):
        for x in range(x0 - 1, x0 + w + 1):
            if y in (y0 - 1, y0 + h) or x in (x0 - 1, x0 + w) or x == x0 + w // 2 or y == y0 + h // 2:
                shade_px(c, x, y, R['white'], .7)
            else:
                shade_px(c, x, y, NOITE, .3 + (y - y0) / h * .5)
    rng = np.random.default_rng(x0)
    for _ in range(3):
        put(c, x0 + rng.integers(1, w - 1), y0 + rng.integers(1, h // 2), hexc('fff3b0'))
    put(c, x0 + w - 3, y0 + 2, hexc('fffbe0')); put(c, x0 + w - 4, y0 + 2, hexc('f8e8a0'))
    put(c, x0 + w - 3, y0 + 3, hexc('f8e8a0'))  # lua
    CORT = ramp('5a2030', '8a3048', 'b04860', 'd07080')
    for y in range(y0 - 3, y0 + h + 3):
        for x in (x0 - 3, x0 - 2, x0 + w + 1, x0 + w + 2):
            shade_px(c, x, y, CORT, .5 + (.2 if (y % 3 == 0) else 0))
    for x in range(x0 - 4, x0 + w + 4):
        shade_px(c, x, y0 - 4, R['wood'], .5)


def estante(c, x0, y0, w, h):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            edge = x in (x0, x0 + w - 1) or y == y0
            shade_px(c, x, y, R['wood'], .35 if edge else .2)
    rng = np.random.default_rng(x0 + 7)
    livros = ['red', 'pink', 'yellow', 'white']
    shelf_h = 9
    for sy in range(y0 + 1, y0 + h - 2, shelf_h):
        for x in range(x0 + 1, x0 + w - 1):
            cor = R[rng.choice(livros)] if rng.random() < .8 else ramp('1a2a5a', '24429a', '3a6ad0', '6a9ae8')
            bh = rng.integers(5, 8)
            for y in range(sy + shelf_h - 1 - bh, sy + shelf_h - 1):
                shade_px(c, x, y, cor, .6 if x % 2 else .4)
        for x in range(x0, x0 + w):
            shade_px(c, x, sy + shelf_h - 1, R['wood'], .7)


def parede_lado(prof_tiles):
    c = parede('#' * prof_tiles)
    # escurece: a parede lateral pega menos luz
    c[:, :, :3] *= 0.78
    return c


def porta(aberta):
    W, H = 16, int(ALTURA_PAREDE * PPU) - 6
    c = canvas(W, H)
    for y in range(H):
        for x in range(W):
            if aberta:
                if x < 3:
                    shade_px(c, x, y, R['wood'], .55 if x == 2 else .35)
                else:
                    put(c, x, y, hexc('0a0808') if y < H - 2 else hexc('2a1a10'))
            else:
                v = .78 + (vnoise(x * .3, y * .08, 6) - .5) * .3
                if x in (0, W - 1) or y == 0:
                    v = .3
                if (4 <= y <= 14 or 20 <= y <= H - 4) and x in (3, 12):
                    v = .3
                shade_px(c, x, y, R['wood'], v)
    if not aberta:
        put(c, 12, H // 2 + 2, R['yellow'][2]); put(c, 12, H // 2 + 3, R['yellow'][1])
    return c
