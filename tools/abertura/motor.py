"""
Mini motor 3D em software (numpy) para a abertura, no estilo HD-2D:
texturas pixeladas (amostragem "nearest"), chão analítico gigante, malhas de triângulos,
billboards virados para a câmera, partículas somadas e pós-processamento
(desfoque de profundidade, bloom, névoa, vinheta, raios de luz).
"""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom


def norm(v):
    return v / np.linalg.norm(v)


class Camera:
    def __init__(self, pos, look, fov=40.0, w=960, h=540):
        self.pos = np.asarray(pos, float)
        self.look = np.asarray(look, float)
        self.fov = fov
        self.w, self.h = w, h
        f = norm(self.look - self.pos)
        r = np.cross([0, 1, 0], f)
        if np.linalg.norm(r) < 1e-6:
            r = np.array([1.0, 0, 0])
        r = norm(r)
        u = np.cross(f, r)
        self.f, self.r, self.u = f, r, u
        self.ty = np.tan(np.radians(fov) / 2)
        self.tx = self.ty * w / h

    def rays(self):
        sx = (np.arange(self.w) + .5) / self.w * 2 - 1
        sy = 1 - (np.arange(self.h) + .5) / self.h * 2
        SX, SY = np.meshgrid(sx, sy)
        D = self.f + SX[..., None] * self.tx * self.r + SY[..., None] * self.ty * self.u
        return SX, SY, D

    def to_cam(self, P):
        d = P - self.pos
        return np.stack([d @ self.r, d @ self.u, d @ self.f], -1)

    def project(self, C):
        """câmera → pixel (x, y), y para baixo."""
        x = (C[..., 0] / (C[..., 2] * self.tx) + 1) * .5 * self.w
        y = (1 - C[..., 1] / (C[..., 2] * self.ty)) * .5 * self.h
        return x, y


class Frame:
    NEAR = 0.15

    def __init__(self, cam, sky_fn, ground_fn=None):
        self.cam = cam
        H, W = cam.h, cam.w
        SX, SY, D = cam.rays()
        self.SX, self.SY = SX, SY
        self.color = sky_fn(D / np.linalg.norm(D, axis=2, keepdims=True))
        self.depth = np.full((H, W), 1e9)  # profundidade ao longo do eixo da câmera
        self.add = np.zeros((H, W, 3))
        self.glow = np.zeros((H, W, 3))  # brilho extra só para o bloom
        if ground_fn is not None:
            down = D[..., 1] < -1e-5
            t = np.where(down, -cam.pos[1] / np.where(down, D[..., 1], -1), 1e9)
            P = cam.pos + D * t[..., None]
            col = ground_fn(P[..., 0], P[..., 2])
            z = t  # D não normalizado: componente em f vale 1 → t já é a profundidade
            m = down & (z < 4000)
            self.color[m] = col[m]
            self.depth[m] = z[m]

    # ---------------------------------------------------------------- triângulos

    def tri(self, P, UV, tex, tint=(1, 1, 1), mode='cut', glow=0.0):
        """P: (3,3) mundo; UV: (3,2) com v=0 no topo da imagem; tex: (h,w,4) 0..1."""
        cam = self.cam
        C = cam.to_cam(P)
        if (C[:, 2] < self.NEAR).any():
            return
        xs, ys = cam.project(C)
        W, H = cam.w, cam.h
        x0, x1 = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
        y0, y1 = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
        if x0 > x1 or y0 > y1:
            return
        gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        px, py = gx + .5, gy + .5
        ax, ay, bx, by, cx, cy = xs[0], ys[0], xs[1], ys[1], xs[2], ys[2]
        area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if abs(area) < 1e-9:
            return
        w0 = ((bx - px) * (cy - py) - (by - py) * (cx - px)) / area
        w1 = ((cx - px) * (ay - py) - (cy - py) * (ax - px)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            return
        iz = 1 / C[:, 2]
        izp = w0 * iz[0] + w1 * iz[1] + w2 * iz[2]
        z = 1 / izp
        u = (w0 * UV[0, 0] * iz[0] + w1 * UV[1, 0] * iz[1] + w2 * UV[2, 0] * iz[2]) * z
        v = (w0 * UV[0, 1] * iz[0] + w1 * UV[1, 1] * iz[1] + w2 * UV[2, 1] * iz[2]) * z
        th, tw = tex.shape[:2]
        iu = np.clip((u * tw).astype(int), 0, tw - 1)
        iv = np.clip((v * th).astype(int), 0, th - 1)
        t = tex[iv, iu]
        sub_d = self.depth[y0:y1 + 1, x0:x1 + 1]
        m = inside & (z < sub_d)
        tint = np.asarray(tint, float)
        if mode == 'add':
            m &= t[..., 3] > 0.01
            self.add[y0:y1 + 1, x0:x1 + 1][m] += t[m, :3] * t[m, 3:4] * tint
            return
        m &= t[..., 3] > .5
        if not m.any():
            return
        self.color[y0:y1 + 1, x0:x1 + 1][m] = t[m, :3] * tint
        sub_d[m] = z[m]
        if glow > 0:
            self.glow[y0:y1 + 1, x0:x1 + 1][m] += t[m, :3] * glow

    def quad(self, O, U, V, tex, tint=(1, 1, 1), mode='cut', glow=0.0):
        """Retângulo: O = canto do topo-esquerdo da imagem, U → direita, V → baixo."""
        O, U, V = (np.asarray(a, float) for a in (O, U, V))
        A, B, Cc, D = O, O + U, O + V, O + U + V
        self.tri(np.array([A, B, Cc]), np.array([[0, 0], [1, 0], [0, 1]]), tex, tint, mode, glow)
        self.tri(np.array([B, D, Cc]), np.array([[1, 0], [1, 1], [0, 1]]), tex, tint, mode, glow)

    def billboard(self, foot, tex, ppu=16, scale=1.0, tint=(1, 1, 1), mode='cut', flip=False, glow=0.0,
                  center=False):
        """Imagem em pé virada para a câmera (gira só no eixo vertical)."""
        foot = np.asarray(foot, float)
        h, w = tex.shape[:2]
        sw, sh = w / ppu * scale, h / ppu * scale
        to_cam = self.cam.pos - foot
        to_cam[1] = 0
        if np.linalg.norm(to_cam) < 1e-6:
            return
        fwd = norm(to_cam)
        right = np.cross([0, 1, 0], fwd) * -1  # direita da imagem vista pela câmera
        right = norm(right)
        if flip:
            tex = tex[:, ::-1]
        base = foot - (np.array([0, sh / 2, 0]) if center else 0)
        O = base - right * sw / 2 + np.array([0, sh, 0])
        self.quad(O, right * sw, np.array([0, -sh, 0]), tex, tint, mode, glow)

    def sprite_screen(self, img, x, y, scale=1, alpha=1.0):
        """Desenha uma imagem 2D direto na tela (para o relógio e o título)."""
        if scale != 1:
            img = np.kron(img, np.ones((scale, scale, 1)))
        h, w = img.shape[:2]
        X0, Y0 = int(x - w / 2), int(y - h / 2)
        H, W = self.cam.h, self.cam.w
        sx0, sy0 = max(0, -X0), max(0, -Y0)
        sx1, sy1 = min(w, W - X0), min(h, H - Y0)
        if sx0 >= sx1 or sy0 >= sy1:
            return
        sub = img[sy0:sy1, sx0:sx1]
        a = sub[..., 3:4] * alpha
        reg = self.color[Y0 + sy0:Y0 + sy1, X0 + sx0:X0 + sx1]
        reg[:] = reg * (1 - a) + sub[..., :3] * a

    # ---------------------------------------------------------------- pós

    def finish(self, focus=20.0, dof=12.0, haze_color=(.9, .75, .62), haze_density=.006, haze_max=.65,
               bloom=0.9, threshold=.78, vignette=.32, saturation=1.15, rays=0.0, rays_angle=-.5,
               grade=(1, 1, 1), shadow_tint=(.04, .03, .1), white=0.0, exposure=1.0, extra_blur=0.0):
        c = self.color
        d = self.depth
        sky = d > 1e8
        hz = np.where(sky, 0, np.clip(1 - np.exp(-d * haze_density), 0, haze_max))
        c = c * (1 - hz[..., None]) + np.asarray(haze_color) * hz[..., None]
        c = c + self.add
        # profundidade de campo
        if dof > 0:
            dd = np.where(sky, 3000, d)
            coc = np.clip(np.abs(1 / dd - 1 / focus) * dof, 0, 1)
            b1 = np.stack([gaussian_filter(c[..., k], 2.2) for k in range(3)], -1)
            b2 = np.stack([gaussian_filter(c[..., k], 5.5) for k in range(3)], -1)
            k1 = np.clip(coc * 2, 0, 1)[..., None]
            k2 = np.clip(coc * 2 - 1, 0, 1)[..., None]
            c = c * (1 - k1) + b1 * k1
            c = c * (1 - k2) + b2 * k2
        if extra_blur > 0:
            c = np.stack([gaussian_filter(c[..., k], extra_blur) for k in range(3)], -1)
        c = c * exposure
        # raios de sol
        if rays > 0:
            from paint import vnoise
            proj = self.SX * np.cos(rays_angle) * (self.cam.w / self.cam.h) + self.SY * np.sin(rays_angle)
            r = vnoise(proj * 7.0, np.zeros_like(proj), 5) ** 3
            r *= np.clip((self.SY + .2) / 1.2, 0, 1)
            c += np.array([1, .82, .55]) * r[..., None] * rays
        # bloom
        if bloom > 0:
            lum = c.max(2)
            br = c * np.clip((lum - threshold) / max(1e-3, 1 - threshold), 0, 1)[..., None] + self.glow
            g = sum(np.stack([gaussian_filter(br[..., k], s) for k in range(3)], -1) * w8
                    for s, w8 in ((3, .8), (10, .7), (28, .5)))
            c = c + g * bloom
        c = c * np.asarray(grade)
        lum = c @ np.array([.299, .587, .114])
        c = lum[..., None] + (c - lum[..., None]) * saturation
        c = c + np.asarray(shadow_tint) * (1 - np.clip(lum, 0, 1))[..., None] ** 2
        c = c / (1 + np.clip(c - 1, 0, None) * .5)  # segura os estouros
        vx, vy = self.SX * .9, self.SY
        vig = np.clip(1 - (vx * vx + vy * vy) * vignette, 0, 1) ** 1.3
        c = c * vig[..., None]
        if white > 0:
            c = c * (1 - white) + white
        return np.clip(c, 0, 1)
