"""
Renderiza a abertura.

  python render.py quadro 58.2 saida.png          # um quadro (para conferir)
  python render.py storyboard saida.png           # quadros-chave lado a lado
  python render.py video saida.mp4 musica.mp3     # vídeo completo (24 fps) com a música
"""
import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, '..', 'arte'))

from motor import Camera, Frame  # noqa: E402
import roteiro as RT  # noqa: E402
import arte_reino as A  # noqa: E402

W, H = 960, 540
FPS = 24
FONTE = os.path.join(AQUI, 'fonte_titulo.otf')
_mundo = None
_relogio = None


def mundo():
    global _mundo
    if _mundo is None:
        from mundo import Mundo
        _mundo = Mundo()
    return _mundo


def ceu(D):
    e = D[..., 1]
    t = np.clip((e + .02) / .5, 0, 1)
    top, mid, hor = np.array([.36, .5, .82]), np.array([.62, .74, .92]), np.array([1.0, .86, .66])
    c = np.where((t < .3)[..., None], hor + (mid - hor) * (t / .3)[..., None],
                 mid + (top - mid) * ((t - .3) / .7)[..., None])
    # sol baixo a oeste-sudoeste (atrás da câmera em boa parte do voo)
    sol = np.array([-.75, .22, -.62])
    sol /= np.linalg.norm(sol)
    d = np.clip(D @ sol, 0, 1)
    c = c + np.array([1, .8, .5]) * (d ** 40 * .8 + d ** 6 * .15)[..., None]
    return c


# ================================================================== relógio

def quadro_relogio(t):
    global _relogio
    if _relogio is None:
        _relogio = A.relogio_base(112)
    base, runas = _relogio
    S = base.shape[0]
    fr = Frame(Camera((0, 0, 0), (0, 0, 1), w=W, h=H), lambda D: np.zeros(D.shape[:2] + (3,)))
    # aparece do escuro
    aparece = np.clip(t / 2.0, 0, 1) ** 1.5
    # ponteiros girando ao contrário, cada vez mais rápido
    vel = 1 + (t / 16) ** 3 * 30
    giro = -(t * vel) * .6
    img = base.copy()
    lum_runas, pulso = RT.runas_acesas(t)
    lay = np.zeros_like(runas)
    for k in range(12):
        ang = -np.pi / 2 + k / 12 * 2 * np.pi
        cx, cy = S / 2 + np.cos(ang) * 21, S / 2 + np.sin(ang) * 21
        y0, y1, x0, x1 = int(cy - 4), int(cy + 5), int(cx - 3), int(cx + 4)
        m = runas[y0:y1, x0:x1, 3] > 0
        acesa = k < lum_runas
        cor = np.array([1, .92, .55]) if acesa else np.array([.32, .22, .46])
        bloco = lay[y0:y1, x0:x1]
        bloco[m, :3] = runas[y0:y1, x0:x1][m, :3] * cor
        bloco[m, 3] = 1
    a = lay[..., 3:4]
    img[..., :3] = img[..., :3] * (1 - a) + lay[..., :3] * a
    pont = A.ponteiros(S, giro / 12, giro, giro * 4)
    pa = pont[..., 3:4]
    img[..., :3] = img[..., :3] * (1 - pa) + pont[..., :3] * pa
    escala = 4
    big = np.kron(img, np.ones((escala, escala, 1)))
    # leve "respiração"
    fr.sprite_screen(big, W / 2, H / 2 + np.sin(t * 1.3) * 3, alpha=aparece)
    # brilho das runas acesas (só para o bloom)
    glow_rune = np.kron(lay[..., :3] * lay[..., 3:4], np.ones((escala, escala, 1)))
    gy0, gx0 = int(H / 2 - big.shape[0] / 2), int(W / 2 - big.shape[1] / 2)
    hh, ww = glow_rune.shape[:2]
    sy0, sx0 = max(0, -gy0), max(0, -gx0)
    fr.glow[gy0 + sy0:gy0 + hh, gx0 + sx0:gx0 + ww] += glow_rune[sy0:H - gy0, sx0:W - gx0] * (.45 + pulso * 1.6) * aparece
    # o relógio inteiro começa a brilhar antes do clarão
    carga = np.clip((t - 13.5) / 2.6, 0, 1) ** 2
    if carga > 0:
        corpo = np.kron(img[..., :3] * img[..., 3:4], np.ones((escala, escala, 1)))
        fr.glow[gy0 + sy0:gy0 + hh, gx0 + sx0:gx0 + ww] += corpo[sy0:H - gy0, sx0:W - gx0] * carga * 3
    white = float(np.clip((t - 15.2) / (RT.REVELA - 15.2), 0, 1)) ** 1.5
    return fr.finish(dof=0, bloom=.9 + carga * 2, threshold=.66, vignette=.5, saturation=1.1, white=white,
                     haze_density=0, rays=0)


# ================================================================== reino

def quadro_reino(t):
    M = mundo()
    pos, look, fov = RT.camera(t)
    cam = Camera(pos, look, fov=fov, w=W, h=H)
    fr = Frame(cam, ceu, lambda x, z: M.chao(x, z, t))
    M.prepare(cam)
    M.desenhar(fr, t, RT.princesa_sorri(t), RT.erupcao(t))
    p = RT.pos_processo(t)
    alvo = np.asarray(look) - pos
    p['focus'] = float(np.linalg.norm(alvo))
    return fr.finish(**p)


# ================================================================== título

def titulo(img, t):
    k = np.clip((t - RT.TITULO) / .9, 0, 1)
    if k <= 0:
        return img
    im = Image.fromarray((img * 255).astype(np.uint8)).convert('RGBA')
    camada = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    f1 = ImageFont.truetype(FONTE, 84)
    f2 = ImageFont.truetype(FONTE, 44)
    linhas = [('Joaquim', f1, H * .36), ('No Reino da Fantasia', f2, H * .52)]
    mascara = Image.new('L', im.size, 0)
    dm = ImageDraw.Draw(mascara)
    for txt, f, y in linhas:
        w = d.textlength(txt, font=f)
        x = (W - w) / 2
        d.text((x, y), txt, font=f, fill=(60, 30, 10, 255), stroke_width=6, stroke_fill=(40, 18, 6, 255), anchor='lm')
        dm.text((x, y), txt, font=f, fill=255, anchor='lm')
    # dourado em degradê dentro das letras
    grad = np.zeros((H, W, 4), np.uint8)
    yy = np.linspace(0, 1, H)[:, None]
    ouro = np.clip(np.stack([1.0 + 0 * yy, .92 - .25 * ((yy * 6) % 1), .55 - .35 * ((yy * 6) % 1)], -1), 0, 1)
    grad[..., :3] = (np.broadcast_to(ouro, (H, W, 3)) * 255).astype(np.uint8)
    grad[..., 3] = np.asarray(mascara)
    ouro_img = Image.fromarray(grad, 'RGBA')
    brilho = mascara.filter(ImageFilter.GaussianBlur(14))
    glow = Image.new('RGBA', im.size, (255, 220, 140, 0))
    glow.putalpha(brilho.point(lambda v: int(v * .9)))
    camada = Image.alpha_composite(camada, ouro_img)
    out = Image.alpha_composite(im, glow)
    alpha = Image.fromarray((np.asarray(camada)[..., 3] * k).astype(np.uint8))
    camada.putalpha(alpha)
    out = Image.alpha_composite(out, camada)
    arr = np.asarray(out.convert('RGB')).astype(float) / 255
    # estrelinhas cintilando em volta do título
    rng = np.random.default_rng(7)
    for i in range(22):
        x, y = rng.uniform(W * .18, W * .82), rng.uniform(H * .26, H * .6)
        fase = rng.uniform(0, 6)
        b = max(0, np.sin(t * 3 + fase)) * k
        if b < .05:
            continue
        r = int(2 + 4 * b)
        for dd in range(-r, r + 1):
            for (xx, yy_) in ((int(x) + dd, int(y)), (int(x), int(y) + dd)):
                if 0 <= xx < W and 0 <= yy_ < H:
                    arr[yy_, xx] = np.clip(arr[yy_, xx] + (1 - abs(dd) / (r + 1)) * b, 0, 1)
    # clarão na batida do título
    flash = np.exp(-(t - RT.TITULO) * 4) * .5
    return np.clip(arr + flash, 0, 1)


def render_t(t):
    img = quadro_relogio(t) if t < RT.REVELA else quadro_reino(t)
    img = titulo(img, t)
    if t > RT.DURACAO - 1.0:  # escurece um pouco no fim (o jogo assume daqui)
        img = img * (1 - (t - (RT.DURACAO - 1.0)) * .35)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def _job(args):
    i, t, pasta = args
    path = os.path.join(pasta, f'{i:05d}.png')
    if os.path.exists(path):
        return
    Image.fromarray(render_t(t)).save(path)
    if i % 48 == 0:
        print(f'quadro {i} ({t:.1f}s)', flush=True)


def main():
    modo = sys.argv[1]
    if modo == 'quadro':
        Image.fromarray(render_t(float(sys.argv[2]))).save(sys.argv[3])
    elif modo == 'storyboard':
        tempos = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else \
            [3, 12.5, 15.9, 18, 33, 52, 58.6, 66, 80, 86, 98, 108, 114, 120, 125.2, 131, 136, 139]
        cols = 3
        th = H // 2
        tw = W // 2
        rows = (len(tempos) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * tw + (cols + 1) * 8, rows * (th + 26) + 8), (16, 16, 24))
        dr = ImageDraw.Draw(sheet)
        fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
        for n, t in enumerate(tempos):
            print('storyboard', t, flush=True)
            im = Image.fromarray(render_t(t)).resize((tw, th), Image.BILINEAR)
            x = 8 + (n % cols) * (tw + 8)
            y = 8 + (n // cols) * (th + 26)
            sheet.paste(im, (x, y))
            dr.text((x + 4, y + th + 3), f'{int(t // 60)}:{t % 60:05.2f}', fill=(255, 220, 140), font=fnt)
        sheet.save(sys.argv[2])
    elif modo == 'video':
        saida, musica = sys.argv[2], sys.argv[3]
        pasta = saida + '_quadros'
        os.makedirs(pasta, exist_ok=True)
        n = int(RT.DURACAO * FPS)
        jobs = [(i, i / FPS, pasta) for i in range(n)]
        procs = int(os.environ.get('PROCS', '2'))
        with Pool(procs) as pool:
            pool.map(_job, jobs, chunksize=4)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(pasta, '%05d.png'),
                        '-i', musica, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '23',
                        '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.0', '-c:a', 'aac', '-b:a', '160k',
                        '-movflags', '+faststart', '-shortest', saida], check=True)
        print('vídeo pronto:', saida)


if __name__ == '__main__':
    main()
