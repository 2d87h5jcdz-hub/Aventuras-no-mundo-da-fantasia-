"""
Roteiro da abertura, sincronizado com a música (60 batidas por minuto, batidas em ~X.16s).
Todos os tempos em segundos do vídeo = segundos da música.
"""
import numpy as np
from mundo import CASTELO, PRINCESA, VULCAO

DURACAO = 139.5
REVELA = 16.16        # o tema entra: luz → reino
ERUPCAO = 58.16       # batida forte: o vulcão explode
SOBE = 126.16         # batida grave: câmera dispara para o céu
TITULO = 134.12       # última batida: título
BATIDAS_RUNAS = [6.16, 8.16, 10.16, 12.16, 14.16, 15.16]


def _orbita():
    """Volta majestosa em torno do castelo (ápice da música, 106 → 121.5), terminando ao sul, de frente para a torre."""
    keys = []
    a0 = np.arctan2(206 - CASTELO[2], -8 - CASTELO[0])      # sai de onde o rasante no mercado termina
    a1 = -np.pi / 2 - 2 * np.pi                             # termina ao sul, perto da torre da princesa
    for t in np.arange(106.16, 121.6, 1.0):
        k = (t - 106.16) / (121.5 - 106.16)
        a = a0 + (a1 - a0) * k
        r = 41 - 10 * k
        h = 19 + 11 * k
        pos = CASTELO + np.array([np.cos(a) * r, h, np.sin(a) * r])
        look = CASTELO + np.array([0, 13, 0]) * (1 - k) + (PRINCESA + [0, 1.4, 0] - CASTELO) * k
        keys.append((t, pos, look, 40 - 4 * k))
    return keys


# (tempo, posição da câmera, ponto que ela olha, abertura em graus)
KEYS = [
    (REVELA, (0, 95, -75), (0, 10, 140), 42),
    (22.0, (0, 52, -48), (0, 5, 55), 42),
    (27.0, (1, 20, -22), (0, 4, 28), 40),
    (30.16, (1, 10.5, -10), (0, 3, 25), 40),
    (36.0, (-1, 9, 32), (0, 3, 72), 40),
    (42.16, (-3, 9.5, 82), (-18, 4, 122), 40),
    (46.5, (-16, 14, 106), (-72, 22, 144), 40),
    (52.16, (-38, 20, 114), (-92, 32, 150), 40),
    (ERUPCAO, (-52, 24, 124), (-92, 40, 150), 42),
    (64.16, (-50, 30, 176), (-92, 36, 150), 42),
    (70.16, (-4, 22, 180), (60, 6, 152), 40),
    (76.16, (54, 13, 140), (110, 2, 150), 40),
    (81.0, (74, 8, 112), (86, 1, 150), 38),
    (86.0, (76, 8, 170), (88, 1, 205), 38),
    (90.5, (80, 9, 214), (98, 2, 240), 38),
    (94.0, (84, 7, 244), (100, 3, 252), 38),
    (97.5, (66, 11, 250), (40, 6, 215), 40),
    (101.0, (26, 6, 206), (0, 3, 206), 40),
    (104.0, (-6, 4.5, 206), (-30, 3.5, 207), 42),
] + _orbita() + [
    (123.6, PRINCESA + (0.4, 1.9, -6.5), PRINCESA + (0, 1.45, 0), 34),
    (125.6, PRINCESA + (0.1, 1.5, -3.6), PRINCESA + (0, 1.4, 0), 32),
    (SOBE, PRINCESA + (0.1, 1.5, -3.4), PRINCESA + (0, 1.4, 0), 32),
    (129.5, (6, 120, 150), (0, 0, 228), 44),
    (TITULO, (0, 210, 92), (0, 0, 205), 46),
    (DURACAO, (0, 222, 86), (0, 0, 205), 46),
]


def _hermite(t, keys, idx):
    ts = np.array([k[0] for k in keys])
    vals = np.array([np.asarray(k[idx], float) for k in keys])
    if t <= ts[0]:
        return vals[0]
    if t >= ts[-1]:
        return vals[-1]
    i = np.searchsorted(ts, t) - 1
    t0, t1 = ts[i], ts[i + 1]
    p0, p1 = vals[i], vals[i + 1]

    def vel(j):
        if j == 0 or j == len(ts) - 1:
            return np.zeros_like(vals[j])
        return (vals[j + 1] - vals[j - 1]) / (ts[j + 1] - ts[j - 1])

    m0, m1 = vel(i) * (t1 - t0), vel(i + 1) * (t1 - t0)
    u = (t - t0) / (t1 - t0)
    h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
    h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1


def camera(t):
    # o voo para o céu acelera de repente (ease-in forte)
    if SOBE < t < 129.5:
        k = (t - SOBE) / (129.5 - SOBE)
        t = SOBE + (129.5 - SOBE) * (k ** 2.2)
    return _hermite(t, KEYS, 1), _hermite(t, KEYS, 2), float(_hermite(t, KEYS, 3))


def princesa_sorri(t):
    return t >= 124.7


def erupcao(t):
    """0 = fumegando; 1 = explosão máxima (na batida de 58s, decaindo)."""
    if t < ERUPCAO - .3:
        return 0.08
    return float(np.clip(1.4 * np.exp(-(t - ERUPCAO) / 3.0), 0.12, 1.0))


def runas_acesas(t):
    """Quantas das 12 runas estão acesas e o 'pulso' de brilho da última batida."""
    n = 0
    pulso = 0.0
    for i, b in enumerate(BATIDAS_RUNAS):
        if t >= b:
            n = 2 * (i + 1)
            pulso = np.exp(-(t - b) * 3)
    return min(n, 12), pulso


def pos_processo(t):
    """Parâmetros de cor/luz de cada momento."""
    p = dict(focus=40, dof=6, haze_color=(.95, .78, .62), haze_density=.003, haze_max=.45, bloom=.85,
             threshold=.8, vignette=.3, saturation=1.18, rays=.18, rays_angle=-.55, grade=(1.04, 1, .95))
    if t < ERUPCAO + 8 and t > 44:
        p.update(haze_color=(.85, .6, .5), rays=.08, bloom=1.0 + erupcao(t) * .6, threshold=.72)
    if 76 < t < 98:
        p.update(rays=.22, saturation=1.25, grade=(1.02, 1.02, 1.0))
    if 104 < t < 126:
        p.update(rays=.3, bloom=1.0)
    if 122 < t < SOBE + .5:
        p.update(dof=14, vignette=.4)
    if t > SOBE:
        p.update(rays=.25, haze_density=.003)
    # clarão branco da passagem relógio → reino
    if REVELA <= t < REVELA + 1.6:
        p['white'] = float(np.clip(1 - (t - REVELA) / 1.6, 0, 1)) ** 1.5
    return p
