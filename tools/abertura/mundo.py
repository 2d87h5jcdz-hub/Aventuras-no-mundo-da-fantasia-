"""O Reino da Fantasia: terreno, floresta, vulcão, praia, vila, castelo — e como desenhar tudo num quadro."""
import numpy as np
import arte_reino as A
from paint import R, ramp, vnoise, fbm, hash2, hexc, BAYER

PX = 6                      # pixels de textura por unidade no chão
X0, X1, Z0, Z1 = -200, 200, -120, 360
CASTELO = np.array([0.0, 0.0, 232.0])
VULCAO = np.array([-92.0, 0.0, 150.0])
VULCAO_R, VULCAO_H = 42.0, 40.0
PRINCESA = np.array([7.0, 26.0, 222.0])
MERCADO = np.array([0.0, 0.0, 206.0])
PORTO_Z = (226.0, 238.0, 250.0)   # cais (píeres) do porto, ao norte da praia


def costa(z):
    return 88 + 6 * np.sin(z * .04) + 3 * np.sin(z * .13 + 1)


def estrada(z):
    return 3 * np.sin(z * .03) + 1.5 * np.sin(z * .09)


def q(rmp, v, xs, ys, dither=1.0):
    n = len(rmp) - 1
    f = np.clip(v, 0, .9999) * n
    i = np.floor(f).astype(int)
    thr = .5 + (BAYER[ys % 4, xs % 4] - .5) * dither
    i = np.where((f - i > thr) & (i < n), i + 1, i)
    return rmp[i]


GRAMA = R['grass']
MATA = ramp('0e2420', '163a30', '1f5038', '2c6a40', '42884a', '6aa858')
CINZA = ramp('1a1414', '2a2220', '3e3430', '574a42', '72645a')
AREIA = ramp('b8955a', 'd4b078', 'e8c890', 'f4dcaa', 'fff0cc')
PEDRA = ramp('4a4a5a', '6a6a7a', '8a8a96', 'a8a8b2', 'c8c6cc')
AGUA = ramp('0a2a5a', '124a86', '1a6aaa', '2a8ac8', '5ab0e0', 'b0e4ff')


class Mundo:
    def __init__(self, seed=1):
        print('gerando terreno...')
        self.rng = np.random.default_rng(seed)
        self._terreno()
        print('montando objetos...')
        self._texturas()
        self._objetos()

    # ------------------------------------------------------------ chão

    def _terreno(self):
        W, H = (X1 - X0) * PX, (Z1 - Z0) * PX
        ys, xs = np.mgrid[0:H, 0:W]
        x = X0 + (xs + .5) / PX
        z = Z1 - (ys + .5) / PX
        n = fbm(xs * .02, ys * .02, 1)
        blade = vnoise(xs * .9, ys * .25, 7)
        col = q(GRAMA, .42 + (n - .5) * .8 + np.where(blade > .74, .25, np.where(blade < .2, -.15, 0)), xs, ys)
        bio = np.zeros((H, W), np.uint8)  # 0 grama, 1 mata, 2 cinza, 3 areia, 4 água, 5 pedra, 6 terra
        # floresta
        fm = (np.abs(x) < 70) & (z > -5) & (z < 112)
        col = np.where(fm[..., None], q(MATA, .38 + (n - .5) * .9 + np.where(blade > .78, .2, 0), xs, ys), col)
        bio[fm] = 1
        # região do vulcão (cinza e rocha)
        dv = np.hypot(x - VULCAO[0], z - VULCAO[2])
        vm = dv < 62 + (n - .5) * 14
        col = np.where(vm[..., None], q(CINZA, .45 + (n - .5) * .9 - np.clip((dv - 40) / 25, 0, 1) * .15, xs, ys), col)
        bio[vm] = 2
        # estrada de terra
        er = (np.abs(x - estrada(z)) < 1.6 + (vnoise(z * 2, 3) - .5) * .4) & (z < 210)
        er |= (np.abs(z - 196 - 4 * np.sin(x * .05)) < 1.4) & (x > 10) & (x < costa(z) - 8)  # estrada para a praia
        col = np.where(er[..., None], q(R['dirt'], .5 + (n - .5) * .6, xs, ys), col)
        bio[er] = 6
        # vila: praça de pedra, anéis e ruas radiais
        dc = np.hypot(x - CASTELO[0], z - CASTELO[2])
        ang = np.arctan2(z - CASTELO[2], x - CASTELO[0])
        rua = (np.abs(dc - 24) < 1.6) | (np.abs(dc - 38) < 1.4)
        rua |= (dc < 50) & (dc > 17) & (np.abs(((ang + np.pi / 8) % (np.pi / 4)) - np.pi / 8) * dc < 1.5)
        praca = (dc < 20) | ((np.abs(x - MERCADO[0]) < 18) & (np.abs(z - MERCADO[2]) < 10))
        pm = praca | rua
        pv = .55 + (vnoise(xs * .5, ys * .5, 3) - .5) * .4 - np.where(((xs // 4 + ys // 4) % 2) == 0, .08, 0)
        pv = np.where((xs % 4 == 0) | (ys % 4 == 0), pv - .25, pv)
        col = np.where(pm[..., None], q(PEDRA, pv, xs, ys), col)
        bio[pm] = 5
        # praia e mar
        cz = costa(z)
        areia = x > cz - 11
        col = np.where(areia[..., None], q(AREIA, .55 + (n - .5) * .5 + np.where(x > cz - 2.5, -.25, 0), xs, ys), col)
        bio[areia] = 3
        porto = (z > PORTO_Z[0] - 8) & (z < PORTO_Z[-1] + 8) & (x > cz - 13) & (x <= cz + .5)
        tab = np.where((xs % 6 == 0) | ((ys + (xs // 6) * 7) % 23 == 0), .25,
                       .62 + (vnoise(xs * .4, ys * .08, 5) - .5) * .3)
        col = np.where(porto[..., None], q(R['wood'], tab, xs, ys, .5), col)
        bio[porto] = 7
        mar = x > cz
        bio[mar] = 4
        col = np.where(mar[..., None], q(AGUA, .5 - np.clip((x - cz) / 60, 0, .35), xs, ys), col)
        # flores nos campos
        flor = (bio == 0) & (hash2(xs, ys, 9) > .994)
        cores = np.array([R['white'][3], R['yellow'][2], R['pink'][2], R['red'][2]])
        col[flor] = cores[(hash2(xs, ys, 3) * 4).astype(int) % 4][flor]
        self.ground = (col * 255).astype(np.uint8)
        self.bio = bio
        self.costa_px = None
        self.W, self.H = W, H

    def chao(self, x, z, t):
        """Cor do chão nas coordenadas do mundo (com o mar animado)."""
        px = np.clip(((x - X0) * PX).astype(int), 0, self.W - 1)
        py = np.clip(((Z1 - z) * PX).astype(int), 0, self.H - 1)
        fora = (x < X0) | (x > X1) | (z < Z0) | (z > Z1)
        col = self.ground[py, px].astype(float) / 255
        b = self.bio[py, px]
        agua = (b == 4) | (fora & (x > 0))
        areia = b == 3
        if areia.any():
            # vai-e-vem da água na areia: espuma branca + areia molhada
            cz = costa(z)
            dist = x - cz
            swash = 1.4 + 1.6 * np.sin(t * .9 + z * .05)
            espuma_areia = areia & (dist > -swash) & (dist <= 0) & (vnoise(z * 2.5, t * .7, 21) > .25)
            molhada = areia & (dist > -swash - 1.6) & (dist <= -swash)
            col = np.where(molhada[..., None], col * np.array([.78, .76, .8]), col)
            col = np.where(espuma_areia[..., None], np.array([.86, .9, .94]), col)
        if agua.any():
            cz = costa(z)
            dist = x - cz
            onda = np.sin(z * 1.3 + x * .4 - t * 2.2) * .5 + .5
            brilho = vnoise(x * 1.5 + t * .6, z * 1.5, 11)
            v = .52 - np.clip(dist / 60, 0, .35) + (onda - .5) * .12 + (brilho > .82) * .35
            espuma = (dist < 1.2 + .6 * np.sin(z * .7 + t * 1.5)) & (dist > 0)
            # cristas de onda andando em direção à praia
            fase = dist * .15 + t * .55 + np.sin(z * .06) * .8
            crista = ((fase % 1) < .05) & (dist > 1.5) & (dist < 32) & (vnoise(z * .25, fase * .5, 31) > .5)
            crista &= ~((z > PORTO_Z[0] - 10) & (z < PORTO_Z[-1] + 10) & (dist < 22))  # água calma no porto
            espuma |= crista
            xs, ys = px, py
            cagua = q(AGUA, v, xs, ys)
            cagua = np.where(espuma[..., None], np.array([.84, .9, .95]), cagua)
            col = np.where(agua[..., None], cagua, col)
        col = np.where((fora & ~agua)[..., None], GRAMA[2], col)
        return col

    # ------------------------------------------------------------ texturas

    def _texturas(self):
        T = {}
        T['arvores'] = A.arvores()
        T['mata'] = A.arvores_mata()
        T['pinheiros'] = [A.pinheiro(s) for s in range(3)]
        T['nuvens'] = [A.nuvem(s) for s in range(4)]
        cores_parede = [('a89a7a', 'd8ccb0', 'f0e6cc', 'fff8e8', 'ffffff'),
                        ('a87a5a', 'd8a07a', 'f0c098', 'fadcbc', 'fff0dc'),
                        ('7a8aa0', 'a0b4cc', 'c4d6ea', 'e0ecf8', 'ffffff'),
                        ('a8a060', 'd8d080', 'f0e8a8', 'fff6cc', 'ffffff'),
                        ('a07a90', 'd0a0bc', 'ecc4d8', 'fae0ec', 'ffffff')]
        cores_telhado = [('3e1a16', '6a2a20', '93402c', 'b85a3a', 'd67c52'),
                         ('101a4a', '1a2a7a', '2a44a8', '4a6ad0', '7a9af0'),
                         ('0a3a2a', '145a40', '208058', '30a870', '60d098'),
                         ('5a3a08', '8a5a10', 'c08a20', 'e8b040', 'ffd870'),
                         ('3a103a', '5a1a5a', '8a2a8a', 'b04ab0', 'd07ad0')]
        T['paredes'] = [A.parede_casa(c, 48, 32, i) for i, c in enumerate(cores_parede)]
        T['paredes_lado'] = [A.parede_casa(c, 32, 32, i + 10, porta=False) for i, c in enumerate(cores_parede)]
        T['telhados'] = [A.telhado_cor(c, 48, 24, i) for i, c in enumerate(cores_telhado)]
        T['pedra'] = A.pedra_castelo(64, 64, 1, True, False)
        T['muralha'] = A.pedra_castelo(96, 48, 2, False, True)
        T['torre'] = A.pedra_castelo(64, 96, 3, True, True)
        T['torre_fechada'] = A.pedra_castelo(64, 96, 4, True, False)
        T['telhado_torre'] = A.telhado_torre()
        T['telhado_castelo'] = A.telhado_torre(('1a1a5a', '2a2a8a', '3a4ac0', '5a70e0', '90a8ff'), 96, 48)
        T['bandeira'] = [A.bandeira(i) for i in range(4)]
        T['portao'] = A.pedra_castelo(16, 16, 9, False, False) * np.array([.35, .3, .28, 1])
        T['topo'] = A.pedra_castelo(16, 16, 7, False, False)
        T['vulcao'], _ = A.textura_vulcao()
        T['montanhas'] = [A.textura_montanha(seed=s) for s in range(3)]
        T['dragao'] = [A.dragao(i) for i in range(3)]
        T['princesa'] = [A.princesa(False, s) for s in range(3)]
        T['princesa_sorri'] = [A.princesa(True, s) for s in range(3)]
        T['guarda_sol'] = [A.guarda_sol(c) for c in ('e04848', '3a8ae0', 'f0c040', '40b070')]
        T['banhistas'] = [A.banhista(t, s) for s in range(4) for t in ('em_pe', 'deitado', 'acenando')]
        T['barco'] = A.barco()
        T['faisca'] = A.faisca()
        T['fumaca'] = [A.fumaca(s) for s in range(3)]
        T['luz'] = A.brilho_runa()
        T['passaro'] = [A.passaro(0), A.passaro(1)]
        T['gaivota'] = [A.passaro(0, True), A.passaro(1, True)]
        T['croc'] = [A.crocodilo(k) for k in range(3)]
        T['carroca'] = [A.carroca(k) for k in range(2)]
        T['aldeao'] = [[A.aldeao(s, 0), A.aldeao(s, 1)] for s in range(16)]
        T['barraca'] = [A.barraca(c, i) for i, c in enumerate(('d04040', '3a6ad0', 'f0c040', '40a060', '9a4ab0'))]
        T['navio'] = [A.navio(s) for s in range(3)]
        T['marinheiro'] = [[A.marinheiro(False, 0), A.marinheiro(False, 1)], [A.marinheiro(True, 0), A.marinheiro(True, 1)]]
        T['caixotes'] = [A.caixotes(s) for s in range(3)]
        T['tabuas'] = A.tabuas()
        self.T = T

    # ------------------------------------------------------------ objetos

    def _objetos(self):
        rng = self.rng
        bb = []  # (x, y, z, kind, idx, scale, flip)
        # floresta densa (com uma clareira no caminho da câmera)
        for z in np.arange(-2, 112, 3.2):
            for x in np.arange(-70, 70, 3.2):
                xx, zz = x + rng.uniform(-1.3, 1.3), z + rng.uniform(-1.3, 1.3)
                if abs(xx - estrada(zz)) < 3.2:
                    continue
                bb.append((xx, 0, zz, 'mata' if rng.random() < .55 else 'arvores', rng.integers(0, 4),
                           rng.uniform(.8, 1.25), rng.random() < .5))
        # campos: árvores espalhadas
        for _ in range(260):
            x, z = rng.uniform(-180, 80), rng.uniform(-100, 340)
            if (abs(x) < 72 and -6 < z < 114) or np.hypot(x - VULCAO[0], z - VULCAO[2]) < 66 \
                    or np.hypot(x - CASTELO[0], z - CASTELO[2]) < 54 or abs(x - estrada(z)) < 4 or x > costa(z) - 14:
                continue
            bb.append((x, 0, z, 'arvores', rng.integers(0, 4), rng.uniform(.9, 1.3), rng.random() < .5))
        # pinheiros perto das montanhas e do vulcão
        for _ in range(220):
            a, r = rng.uniform(0, 2 * np.pi), rng.uniform(64, 95)
            x, z = VULCAO[0] + np.cos(a) * r, VULCAO[2] + np.sin(a) * r
            if np.hypot(x - CASTELO[0], z - CASTELO[2]) < 54 or (abs(x) < 72 and z < 114):
                continue
            bb.append((x, 0, z, 'pinheiros', rng.integers(0, 3), rng.uniform(1, 1.5), rng.random() < .5))
        self.bb = bb
        self.bb_arr = np.array([(b[0], b[1], b[2]) for b in bb])

        # praia: guarda-sóis, banhistas, barcos
        praia = []
        for k in range(26):
            z = 130 + k * 4.5 + rng.uniform(-1.5, 1.5)
            x = costa(z) - rng.uniform(3, 9)
            if k % 3 == 0:
                praia.append((x, 0, z, 'guarda_sol', rng.integers(0, 4), 1.0))
            praia.append((x + rng.uniform(-1.5, 1.5), 0, z + rng.uniform(-1, 1), 'banhistas', rng.integers(0, 12), 1.0))
        for k in range(5):
            z = 140 + k * 22
            praia.append((costa(z) + 14 + rng.uniform(0, 20), 0, z, 'barco', 0, 1.6))
        self.praia = praia

        # casas da vila em anéis em volta do castelo
        casas = []
        for anel, (r, n) in enumerate(((31, 12), (45, 18))):
            for k in range(n):
                a = (k + .5) / n * 2 * np.pi + anel * .1
                # não bloqueia ruas radiais
                if abs(((a + np.pi / 8) % (np.pi / 4)) - np.pi / 8) * r < 3.5:
                    continue
                cx, cz = CASTELO[0] + np.cos(a) * r, CASTELO[2] + np.sin(a) * r
                if abs(cx - MERCADO[0]) < 21 and abs(cz - MERCADO[2]) < 13:
                    continue
                w, d, h = rng.uniform(4.5, 6.5), rng.uniform(4, 5.5), rng.uniform(3, 4.2)
                casas.append((cx, cz, a + np.pi, w, d, h, rng.integers(0, 5), rng.integers(0, 5)))
        self.casas = casas
        # revoadas saindo das árvores durante o voo sobre a floresta
        self.revoadas = []
        for (t0, x, z) in ((31.0, -7, 30), (33.6, 9, 46), (36.4, -11, 62), (39.0, 6, 80), (42.0, -6, 96)):
            aves = [(rng.uniform(-3, 3), rng.uniform(0, 1.5), rng.uniform(-3, 3), rng.uniform(5, 8),
                     rng.uniform(-1, 1), rng.uniform(.8, 1.4)) for _ in range(11)]
            self.revoadas.append((t0, np.array([x, 7.5, z]), aves))
        # bandos no céu (formação em V) e gaivotas na praia e no porto
        self.bandos = [(16.0, np.array([-80, 46, 40]), np.array([7, .3, 4]), 9),
                       (40.0, np.array([-60, 30, 120]), np.array([6, .2, 1]), 7),
                       (60.0, np.array([-20, 34, 175]), np.array([7, 0, -2]), 9),
                       (98.0, np.array([40, 34, 250]), np.array([-6, .2, -2]), 8)]
        self.gaivotas = [(rng.uniform(80, 104), rng.uniform(10, 22), rng.uniform(110, 260), rng.uniform(4, 9),
                          rng.uniform(0, 6)) for _ in range(20)]
        # mercado: duas fileiras de barracas e o povo em volta
        self.barracas = []
        for fila, z in enumerate((MERCADO[2] - 4, MERCADO[2] + 4)):
            for i, x in enumerate(np.arange(-14, 15, 4.2)):
                self.barracas.append((x + rng.uniform(-.4, .4), z + rng.uniform(-.3, .3), (i + fila * 2) % 5))
        self.povo = []
        for _ in range(46):
            self.povo.append(('parado', MERCADO[0] + rng.uniform(-16, 16),
                              MERCADO[2] + rng.choice([-6.5, -1.5, 1.5, 6.5]) + rng.uniform(-1, 1),
                              rng.integers(0, 16), rng.uniform(0, 6)))
        for _ in range(60):
            r = rng.choice([24.0, 38.0])
            self.povo.append(('anel', r, rng.uniform(0, 2 * np.pi), rng.integers(0, 16),
                              rng.choice([-1, 1]) * rng.uniform(.8, 1.4) / r))
        for _ in range(14):
            self.povo.append(('estrada', rng.uniform(14, 70), rng.choice([-1, 1]) * rng.uniform(.8, 1.3),
                              rng.integers(0, 16), 0))
        self.carrocas = [(24.0, .2, 2.6), (38.0, 2.4, -2.3), (38.0, 4.5, 2.4), (24.0, 3.6, -2.5)]
        # porto: navios atracados, pilhas de caixotes e marinheiros indo e vindo
        self.navios = []
        self.marinheiros = []
        self.pilhas = []
        for i, pz in enumerate(PORTO_Z):
            cz_ = costa(pz)
            self.navios.append((cz_ + 15, pz + 3.2, i))
            self.pilhas += [(cz_ - 6 + rng.uniform(-2, 2), pz + rng.uniform(-3, 3), rng.integers(0, 3)) for _ in range(3)]
            for k in range(4):
                self.marinheiros.append((pz + rng.uniform(-.6, .6), cz_ - 5, cz_ + 13, rng.uniform(0, 1),
                                         rng.uniform(.10, .16)))
        self.nuvens = [(rng.uniform(-200, 200), rng.uniform(70, 120), rng.uniform(-60, 380), rng.integers(0, 4),
                        rng.uniform(3, 6)) for _ in range(40)]
        self.montanhas = [(-180, 250, 60, 64, 0), (-130, 330, 70, 78, 1), (-60, 360, 55, 60, 2), (30, 380, 65, 66, 0),
                          (110, 370, 60, 58, 1), (-190, 140, 55, 50, 2), (-170, 40, 50, 44, 1)]

    # ================================================================ desenho

    def desenhar(self, fr, t, princesa_sorri=False, erupcao=0.0):
        cam = fr.cam
        T = self.T
        self._montanhas(fr)
        self._vulcao(fr, t, erupcao)
        self._castelo(fr, t, princesa_sorri)
        self._casas(fr)
        self._billboards(fr)
        self._praia(fr, t)
        self._dragao(fr, t)
        self._vida(fr, t)
        self._porto(fr, t)
        self._nuvens(fr, t)

    def _visivel(self, P, margem=30, maxd=420):
        C = (P - self.cam_pos) @ self.cam_f
        return (C > .3) & (C < maxd)

    def prepare(self, cam):
        self.cam_pos, self.cam_f = cam.pos, cam.f

    def _billboards(self, fr):
        cam = fr.cam
        P = self.bb_arr
        C = cam.to_cam(P)
        ok = (C[:, 2] > .5) & (C[:, 2] < 380) & (np.abs(C[:, 0]) < C[:, 2] * cam.tx + 10) \
            & (C[:, 1] < C[:, 2] * cam.ty + 10) & (C[:, 1] > -C[:, 2] * cam.ty - 20)
        idx = np.where(ok)[0]
        idx = idx[np.argsort(-C[idx, 2])]  # de trás pra frente (ajuda pouco, mas barato)
        for i in idx:
            x, y, z, kind, k, s, flip = self.bb[i]
            fr.billboard((x, y, z), self.T[kind][k], scale=s, flip=flip, tint=(1, .93, .82))

    def _cone(self, fr, cx, cz, r0, r1, h, tex, n=28, tint=(1, 1, 1), y0=0.0, glow=0.0, jag=0.0, seed=0):
        ang = np.linspace(0, 2 * np.pi, n + 1)
        if jag > 0:  # contorno irregular (montanhas)
            rr = np.random.default_rng(seed)
            jb = 1 + rr.uniform(-jag, jag, n)
            jb = np.append(jb, jb[0])
            jt = 1 + rr.uniform(-jag * 2, jag * 2, n)
            jt = np.append(jt, jt[0])
            dh = rr.uniform(-h * jag * .6, h * jag * .3, n)
            dh = np.append(dh, dh[0])
        else:
            jb = jt = np.ones(n + 1)
            dh = np.zeros(n + 1)
        for i in range(n):
            a0, a1 = ang[i], ang[i + 1]
            b0 = np.array([cx + np.cos(a0) * r0 * jb[i], y0, cz + np.sin(a0) * r0 * jb[i]])
            b1 = np.array([cx + np.cos(a1) * r0 * jb[i + 1], y0, cz + np.sin(a1) * r0 * jb[i + 1]])
            rt0, rt1 = max(r1, r0 * .12 * jag) * jt[i], max(r1, r0 * .12 * jag) * jt[i + 1]
            t0 = np.array([cx + np.cos(a0) * rt0, y0 + h + dh[i], cz + np.sin(a0) * rt0])
            t1 = np.array([cx + np.cos(a1) * rt1, y0 + h + dh[i + 1], cz + np.sin(a1) * rt1])
            u0, u1 = i / n, (i + 1) / n
            # luz simples: lado virado para o sol (oeste-sudoeste) mais claro
            mid = (a0 + a1) / 2
            lum = .72 + .28 * np.cos(mid - np.radians(200))
            tt = np.asarray(tint) * lum
            fr.tri(np.array([t0, t1, b0]), np.array([[u0, 0], [u1, 0], [u0, 1]]), tex, tt, glow=glow)
            if r1 > 1e-3:
                fr.tri(np.array([t1, b1, b0]), np.array([[u1, 0], [u1, 1], [u0, 1]]), tex, tt, glow=glow)
            else:
                fr.tri(np.array([t1, b1, b0]), np.array([[u1, 0], [u1, 1], [u0, 1]]), tex, tt, glow=glow)

    def _montanhas(self, fr):
        for i, (x, z, r, h, k) in enumerate(self.montanhas):
            self._cone(fr, x, z, r, 0.01, h, self.T['montanhas'][k], n=22, tint=(.85, .85, .95), jag=.28, seed=i)
            # pico vizinho menor
            self._cone(fr, x + r * .55, z - r * .2, r * .6, 0.01, h * .62, self.T['montanhas'][(k + 1) % 3], n=16,
                       tint=(.8, .8, .92), jag=.3, seed=i + 50)

    def _vulcao(self, fr, t, erupcao):
        cx, cz = VULCAO[0], VULCAO[2]
        self._cone(fr, cx, cz, VULCAO_R, 6, VULCAO_H, self.T['vulcao'], n=32, glow=.25 + erupcao * .4)
        top = np.array([cx, VULCAO_H, cz])
        # cratera brilhando
        fr.billboard(top + [0, -2, 0], self.T['luz'], ppu=1.2, mode='add', tint=(1.2, .5, .15), center=True)
        # lava saltando e fumaça
        rng = np.random.default_rng(int(t * 24) // 3)
        n_lava = int(10 + erupcao * 70)
        base = np.random.default_rng(5)
        for k in range(n_lava):
            ph = base.uniform(0, 3)
            vel = base.uniform(10, 22) * (1 + erupcao * .8)
            ang = base.uniform(0, 2 * np.pi)
            spread = base.uniform(1, 6) * (1 + erupcao)
            tt = (t + ph) % 3.0
            p = top + np.array([np.cos(ang) * spread * tt, vel * tt - 9.8 * tt * tt, np.sin(ang) * spread * tt])
            if p[1] < VULCAO_H - 6:
                continue
            fr.billboard(p, self.T['faisca'], ppu=8, scale=1 + erupcao, mode='add', tint=(1.4, .8, .4), center=True)
        for k in range(10):
            ph = k / 10 * 8
            tt = (t + ph) % 8
            p = top + np.array([np.sin(k * 2.1 + tt * .3) * 3, 2 + tt * 4.5, np.cos(k * 1.7) * 3 + tt * 1.5])
            fr.billboard(p, self.T['fumaca'][k % 3], ppu=2.2, scale=.6 + tt * .25, tint=(.9, .85, .85), center=True)

    def _castelo(self, fr, t, sorri):
        T = self.T
        cx, cz = CASTELO[0], CASTELO[2]
        S = 15.0
        # muralha (quatro lados)
        for (ax, az, bx, bz) in ((-S, -S, S, -S), (S, -S, S, S), (S, S, -S, S), (-S, S, -S, -S)):
            O = np.array([cx + ax, 6.0, cz + az])
            U = np.array([bx - ax, 0, bz - az])
            fr.quad(O, U, [0, -6, 0], T['muralha'], tint=(1, .95, .88))
        # portão
        fr.quad([cx - 2.5, 4.2, cz - S - .05], [5, 0, 0], [0, -4.2, 0], T['portao'])
        # torres dos cantos
        for (sx, sz) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            tx, tz = cx + sx * S, cz + sz * S
            self._cone(fr, tx, tz, 3.2, 3.2, 12, T['torre_fechada'], n=12, tint=(1, .95, .88))
            self._cone(fr, tx, tz, 3.9, .01, 6.5, T['telhado_torre'], n=12, y0=12)
            fr.billboard((tx, 18.3, tz), T['bandeira'][int(t * 6 + sx * 2) % 4], scale=1.4)
        # torreão central
        kx0, kx1, kz0, kz1, kh = cx - 8, cx + 8, cz + 2, cz + 12, 16
        for (ax, az, bx, bz) in ((kx0, kz0, kx1, kz0), (kx1, kz0, kx1, kz1), (kx1, kz1, kx0, kz1), (kx0, kz1, kx0, kz0)):
            fr.quad([ax, kh, az], [bx - ax, 0, bz - az], [0, -kh, 0], T['pedra'], tint=(1, .95, .88))
        # telhado do torreão (duas águas)
        ridge = kh + 7
        fr.quad([kx0, ridge, (kz0 + kz1) / 2], [16, 0, 0], [0, kh - ridge, kz0 - (kz0 + kz1) / 2], T['telhado_castelo'])
        fr.quad([kx1, ridge, (kz0 + kz1) / 2], [-16, 0, 0], [0, kh - ridge, kz1 - (kz0 + kz1) / 2], T['telhado_castelo'],
                tint=(.8, .8, .9))
        for xx in (kx0, kx1):
            fr.tri(np.array([[xx, ridge, (kz0 + kz1) / 2], [xx, kh, kz0], [xx, kh, kz1]]),
                   np.array([[.5, 0], [0, 1], [1, 1]]), T['pedra'], (.9, .85, .8))
        for k, xx in enumerate((kx0 + 2, kx1 - 2)):
            self._cone(fr, xx, kz1 - 1, 2, 2, 22, T['torre_fechada'], n=10, tint=(1, .95, .88))
            self._cone(fr, xx, kz1 - 1, 2.6, .01, 6, T['telhado_torre'], n=10, y0=22)
            fr.billboard((xx, 28, kz1 - 1), T['bandeira'][int(t * 6 + k) % 4], scale=1.6)
        # torre da princesa (topo aberto com ameias)
        px, py, pz = PRINCESA
        self._cone(fr, px, pz, 3.4, 3.4, py, T['torre'], n=14, tint=(1, .95, .88))
        self._cone(fr, px, pz, 3.6, 3.6, 1.2, T['muralha'], n=14, y0=py - .05, tint=(1, .95, .88))
        # piso do topo
        fr.quad([px - 3.4, py, pz + 3.4], [6.8, 0, 0], [0, 0, -6.8], T['topo'], tint=(.95, .9, .85))
        # a princesa
        k = int(t * 3) % 3
        tex = T['princesa_sorri'][k] if sorri else T['princesa'][k]
        fr.billboard((px, py, pz), tex, scale=1.0, tint=(1.04, 1, .96))

    def _casas(self, fr):
        for (cx, cz, yaw, w, d, h, cw, cr) in self.casas:
            self._casa_caixa(fr, cx, cz, yaw, w, d, h, cw, cr)

    def _casa_caixa(self, fr, cx, cz, yaw, w, d, h, cw, cr):
        T = self.T
        if True:
            if ((np.array([cx, 2, cz]) - fr.cam.pos) @ fr.cam.f) < .5:
                return
            fwd = np.array([np.cos(yaw), 0, np.sin(yaw)])     # frente da casa (para o castelo)
            rgt = np.array([-fwd[2], 0, fwd[0]])
            c = np.array([cx, 0, cz])
            fl, fr_, bl, br = (c + fwd * d / 2 - rgt * w / 2, c + fwd * d / 2 + rgt * w / 2,
                               c - fwd * d / 2 - rgt * w / 2, c - fwd * d / 2 + rgt * w / 2)
            up = np.array([0, h, 0])
            parede, lado, telhado = T['paredes'][cw], T['paredes_lado'][cw], T['telhados'][cr]
            fr.quad(fl + up, fr_ - fl, -up, parede, tint=(1, .95, .86))
            fr.quad(br + up, bl - br, -up, parede, tint=(.82, .78, .74))
            fr.quad(bl + up, fl - bl, -up, lado, tint=(.9, .86, .8))
            fr.quad(fr_ + up, br - fr_, -up, lado, tint=(.9, .86, .8))
            rh = h + w * .42
            ridge_l, ridge_r = c - rgt * (w / 2 + .3) + [0, rh, 0], c + rgt * (w / 2 + .3) + [0, rh, 0]
            ov = fwd * (d / 2 + .4)
            fr.quad(ridge_l, ridge_r - ridge_l, ov + [0, h - rh - .2, 0], telhado, tint=(1, .95, .9))
            fr.quad(ridge_r, ridge_l - ridge_r, -ov + [0, h - rh - .2, 0], telhado, tint=(.78, .75, .78))
            for side, s in ((fwd * d / 2, 1), (-fwd * d / 2, -1)):
                fr.tri(np.array([c + side + [0, rh, 0], c + side - rgt * w / 2 + up, c + side + rgt * w / 2 + up]),
                       np.array([[.5, 0], [0, 1], [1, 1]]), lado, (.95, .9, .84))

    def _praia(self, fr, t):
        for (x, y, z, kind, k, s) in self.praia:
            if kind == 'barco':
                z = z + np.sin(t * .2 + x) * 2
                y = .1 * np.sin(t * 1.3 + z)
            fr.billboard((x, y, z), self.T[kind][k] if kind != 'barco' else self.T['barco'], scale=s, tint=(1, .95, .86))

    def posicao_dragao(self, t):
        # fase escolhida para ele cruzar na frente da câmera durante a erupção (~56s)
        a = t * .32 + (-0.55 - 56 * .32)
        return VULCAO + np.array([np.cos(a) * 36, 44 + np.sin(t * .8) * 4, np.sin(a) * 28]), a

    def _dragao(self, fr, t):
        p, a = self.posicao_dragao(t)
        vel = np.array([-np.sin(a), 0, np.cos(a)])
        if 51 < t < 63:
            # rasante na frente da câmera durante a erupção (da esquerda para a direita da tela)
            k = (t - 51) / 12
            topo = VULCAO + np.array([0, VULCAO_H + 4, 0])
            base = fr.cam.pos + (topo - fr.cam.pos) * .42
            p = base + fr.cam.r * (-15 + 30 * k) + np.array([0, 3 * np.sin(k * np.pi) - 1, 0])
            vel = fr.cam.r
        tela = vel @ fr.cam.r  # indo para a direita da tela?
        quadro = [0, 1, 2, 1][int(t * 7) % 4]
        fr.billboard(p, self.T['dragao'][quadro], scale=4.6, flip=tela < 0, center=True, tint=(1, .92, .85))

    def _nuvens(self, fr, t):
        if fr.cam.f[1] < -.55:  # olhando muito para baixo: nuvem "em pé" viraria um risco
            return
        for (x, y, z, k, s) in self.nuvens:
            fr.billboard((x + t * .8, y, z), self.T['nuvens'][k], ppu=4, scale=s * .6, tint=(1, .96, .92), center=True)


    # ------------------------------------------------------------ vida no reino

    def _vida(self, fr, t):
        T = self.T
        # revoadas: os pássaros saem do meio das árvores quando a câmera chega
        for (t0, base, aves) in self.revoadas:
            dt = t - t0
            if dt < 0 or dt > 12:
                continue
            for i, (ox, oy, oz, vz, vx, vy) in enumerate(aves):
                p = base + np.array([ox + vx * dt * 2, oy + dt * (2.2 * vy) + dt * dt * .25, oz + vz * dt])
                fr.billboard(p, T['passaro'][int(t * 9 + i) % 2], scale=1.5, center=True)
        for (t0, origem, vel, n) in self.bandos:
            dt = t - t0
            if dt < 0 or dt > 30:
                continue
            dirv = vel / np.linalg.norm(vel)
            lado = np.cross([0, 1, 0], dirv)
            for i in range(n):
                k = (i + 1) // 2 * (1 if i % 2 else -1)
                p = origem + vel * dt - dirv * abs(k) * 1.6 + lado * k * 1.6 + np.array([0, np.sin(t * 2 + i) * .3, 0])
                fr.billboard(p, T['passaro'][int(t * 7 + i) % 2], scale=2.0, center=True)
        for i, (x, y, z, r, fase) in enumerate(self.gaivotas):
            a = t * .35 + fase
            p = np.array([x + np.cos(a) * r, y + np.sin(t * .9 + i) * 1.5, z + np.sin(a) * r])
            fr.billboard(p, T['gaivota'][int(t * 5 + i) % 2], scale=1.6, center=True)
        # crocodilo bípede cruzando a estrada da esquerda para a direita
        if 32.5 < t < 42.0:
            k = (t - 32.5) / 9.5
            z = 72.0
            x = estrada(z) - 11 + 22 * k
            quadro = [0, 1, 2, 1][int(t * 5) % 4]
            fr.billboard((x, 0, z), T['croc'][quadro], scale=1.7, flip=fr.cam.r[0] < 0, tint=(1, .94, .85))
        # mercado
        for (x, z, c) in self.barracas:
            fr.billboard((x, 0, z), T['barraca'][c], scale=1.1, tint=(1, .95, .86))
        for (tipo, a, b, c, d) in self.povo:
            if tipo == 'parado':
                p = (a, abs(np.sin(t * 2 + d)) * .06, b)
                tex = T['aldeao'][c][0]
            elif tipo == 'anel':
                ang = b + d * t
                p = (CASTELO[0] + np.cos(ang) * a, 0, CASTELO[2] + np.sin(ang) * a)
                tex = T['aldeao'][c][int(t * 4 + b * 10) % 2]
            else:
                x = 14 + (a - 14 + b * t) % 56
                p = (x, 0, 196 + 4 * np.sin(x * .05) + (.6 if b > 0 else -.6))
                tex = T['aldeao'][c][int(t * 4 + a) % 2]
            fr.billboard(p, tex, scale=1.0, tint=(1, .95, .86))
        for i, (r, a0, v) in enumerate(self.carrocas):
            ang = a0 + v / r * t
            p = np.array([CASTELO[0] + np.cos(ang) * r, 0, CASTELO[2] + np.sin(ang) * r])
            vel = np.array([-np.sin(ang), 0, np.cos(ang)]) * np.sign(v)
            fr.billboard(p, T['carroca'][int(t * 5 + i) % 2], scale=1.15, flip=(vel @ fr.cam.r) < 0,
                         tint=(1, .95, .86))

    def _porto(self, fr, t):
        T = self.T
        for pz in PORTO_Z:
            cz_ = costa(pz)
            # píer de tábuas sobre a água, com estacas
            fr.quad([cz_ - 1, .55, pz + 1.3], [16, 0, 0], [0, 0, -2.6], T['tabuas'], tint=(1, .94, .86))
            for xx in np.arange(cz_ + 1, cz_ + 15.5, 3.5):
                for dz in (-1.2, 1.2):
                    fr.billboard((xx, -.3, pz + dz), T['tabuas'][:8, :4], ppu=6, tint=(.6, .5, .45))
        # armazém do porto (caixa com telhado)
        cz_ = costa(PORTO_Z[1])
        self._casa_caixa(fr, cz_ - 9, PORTO_Z[1], 0.0, 10, 7, 5, 0, 0)
        for (x, z, k) in self.pilhas:
            fr.billboard((x, .05, z), T['caixotes'][k], scale=1.1, tint=(1, .95, .86))
        for (x, z, k) in self.navios:
            balanco = np.sin(t * 1.1 + k) * .15
            fr.billboard((x, -1.2 + balanco, z), T['navio'][k], scale=1.7, tint=(.86, .82, .76))
        # marinheiros levando caixotes do cais até o navio e voltando
        for i, (z, x0, x1, fase, vel) in enumerate(self.marinheiros):
            u = (t * vel + fase) % 2.0
            indo = u < 1.0
            k = u if indo else 2.0 - u
            x = x0 + (x1 - x0) * k
            y = .55 if x > costa(z) - 1 else 0.02
            quadro = int(t * 5 + i) % 2
            fr.billboard((x, y, z), T['marinheiro'][1 if indo else 0][quadro], scale=1.0,
                         flip=((1 if indo else -1) * fr.cam.r[0]) < 0, tint=(1, .95, .86))
