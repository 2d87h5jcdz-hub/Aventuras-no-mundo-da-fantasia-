# Vídeo de abertura

Gera `Assets/StreamingAssets/abertura.mp4`: o relógio com runas, o voo pelo Reino da Fantasia
(floresta, vulcão com dragão, praia, vila, castelo e a princesa) e o título — sincronizado com a música.

```
pip install numpy pillow scipy
python tools/abertura/render.py storyboard storyboard.png      # quadros-chave para conferir
python tools/abertura/render.py quadro 58.2 teste.png          # um quadro (tempo em segundos)
python tools/abertura/render.py video abertura.mp4 musica.mp3  # vídeo completo (demora ~1h)
```

| Arquivo | O quê |
|---|---|
| `roteiro.py` | tempos (batidas da música), caminho da câmera, cor de cada momento |
| `mundo.py` | o reino: terreno, floresta, vulcão, praia, vila, castelo, dragão, nuvens |
| `arte_reino.py` | pixel art: relógio e runas, princesa, dragão, casas, castelo, pinheiros... |
| `motor.py` | mini motor 3D em software (estilo HD-2D: desfoque, bloom, névoa, raios de luz) |
| `fonte_titulo.otf` | TeX Gyre Bonum Bold (licença GUST, livre) |
