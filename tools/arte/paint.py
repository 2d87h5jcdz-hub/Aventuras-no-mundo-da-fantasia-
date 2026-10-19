"""Pintura procedural de pixel art com rampas de cor e pontilhado (dither)."""
import numpy as np

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def ramp(*hexes):
    return np.array([hexc(h) for h in hexes])


R = {
    'grass': ramp('1f3d2c', '2d5a35', '42803f', '62a04a', '8fc25a', 'c4dc72'),
    'dirt': ramp('5a3f2a', '7a5636', '9a7048', 'b88c5e', 'd4ad7c'),
    'plaster': ramp('9c8466', 'c2a984', 'dcc59c', 'eedcb6', 'fbf0d6'),
    'wood': ramp('2e1b12', '4a2c1a', '6b4226', '8e5a32', 'b07a46'),
    'roof': ramp('3e1a16', '6a2a20', '93402c', 'b85a3a', 'd67c52', 'eda070'),
    'leaf': ramp('122a22', '1d4030', '2c5c38', '427c3e', '64a04a', '9cc85e', 'd2e488'),
    'leaf_far': ramp('1c2a3a', '263a48', '334c52', '42605a'),
    'bark': ramp('2a1a14', '43291c', '5e3a24', '7c5030'),
    'stone': ramp('3a3a46', '5a5866', '7c7a86', 'a2a0a8', 'c8c4c4'),
    'glass': ramp('5a3a5a', 'a85a5a', 'e89a6a', 'f8cf86', 'fff0c0'),
    'skin': ramp('8a4a34', 'c47a58', 'eba882', 'f8cfa8'),
    'hair': ramp('1e120e', '3a2216', '5a3820', '7a5030'),
    'shirt': ramp('5a6a8a', '9aaac2', 'd8e2ec', 'ffffff'),
    'shorts': ramp('16204a', '24346e', '3a52a0', '5a78c8'),
    'bag': ramp('4a1420', '7a2430', 'a8384a', 'd05a64'),
    'red': ramp('5a1020', '9a2030', 'd04040', 'f07860'),
    'pink': ramp('7a2a5a', 'c04a7a', 'f07aa0', 'ffb0c8'),
    'yellow': ramp('8a5a10', 'd09a20', 'f8d040', 'fff4a0'),
    'white': ramp('8a8aa0', 'c8c8d8', 'f0f0f8', 'ffffff'),
    'iron': ramp('101418', '222a30', '38444c', '58666e'),
}


def canvas(w, h):
    return np.zeros((h, w, 4))


def put(c, x, y, col, a=1.0):
    h, w = c.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        c[y, x, :3] = col
        c[y, x, 3] = a


def shade_px(c, x, y, rmp, v, dither=1.0):
    """v em 0..1, quantizado na rampa com pontilhado ordenado (dither=0 → faixas lisas)."""
    n = len(rmp) - 1
    f = np.clip(v, 0, 0.9999) * n
    i = int(f)
    frac = f - i
    thr = 0.5 + (BAYER[y % 4, x % 4] - 0.5) * dither
    if frac > thr and i < n:
        i += 1
    put(c, x, y, rmp[i])


def hash2(x, y, s=0):
    v = np.sin(x * 127.1 + y * 311.7 + s * 74.7) * 43758.5453
    return v - np.floor(v)


def vnoise(x, y, s=0):
    xi, yi = np.floor(x), np.floor(y)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a, b = hash2(xi, yi, s), hash2(xi + 1, yi, s)
    c, d = hash2(xi, yi + 1, s), hash2(xi + 1, yi + 1, s)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def fbm(x, y, s=0, oct=4):
    t, amp, tot = 0.0, 0.5, 0.0
    for o in range(oct):
        t += vnoise(x, y, s + o * 13) * amp
        tot += amp
        x, y, amp = x * 2.03, y * 2.03, amp * 0.5
    return t / tot


def outline(c, col=(0.08, 0.06, 0.1)):
    """Contorno escuro de 1px em volta do que é opaco (estilo sprite)."""
    a = c[:, :, 3] > 0.5
    pad = np.pad(a, 1)
    nb = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    edge = nb & ~a
    c[edge, :3] = col
    c[edge, 3] = 1.0
    return c


def blob(c, cx, cy, r, rmp, light=(-0.6, -0.8), s=0, ry=None, rough=0.25, base=0.0):
    """Massa arredondada (copa/arbusto) sombreada pela direção da luz."""
    ry = ry or r
    h, w = c.shape[:2]
    lx, ly = light
    for y in range(max(0, int(cy - ry - 2)), min(h, int(cy + ry + 2))):
        for x in range(max(0, int(cx - r - 2)), min(w, int(cx + r + 2))):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / ry
            d = np.hypot(dx, dy)
            edge = 1 + (vnoise(x * 0.45, y * 0.45, s) - 0.5) * rough * 2
            if d > edge:
                continue
            nz = np.sqrt(max(0.0, 1 - min(1.0, d * d)))
            lam = max(0.0, -(dx * lx + dy * ly) * 0.7 + nz * 0.55)
            lam += (vnoise(x * 0.9, y * 0.9, s + 5) - 0.5) * 0.35
            shade_px(c, x, y, rmp, np.clip(base + lam, 0, 1))
