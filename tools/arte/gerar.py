"""
Gera toda a arte do jogo em PNG dentro de Assets/Resources/Art.

Uso (na raiz do projeto):
    pip install numpy pillow
    python tools/arte/gerar.py

Os mapas são lidos de Assets/Scripts/World/Maps.cs, então ao mudar um mapa
basta rodar de novo para o chão/paredes acompanharem.
"""
import os
import sys
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
SAIDA = os.path.join(RAIZ, 'Assets', 'Resources', 'Art')

import cenarios as C  # noqa: E402
import objetos as O  # noqa: E402
import personagens as P  # noqa: E402


def salvar(pasta, nome, arr):
    d = os.path.join(SAIDA, pasta)
    os.makedirs(d, exist_ok=True)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).round().astype('uint8'), 'RGBA')
    img.save(os.path.join(d, nome + '.png'), optimize=True)


def main():
    mapas = C.ler_mapas(os.path.join(RAIZ, 'Assets', 'Scripts', 'World', 'Maps.cs'))

    # ---------------- personagens
    for nome, arr in P.sprites_joaquim().items():
        salvar('Personagens', nome, arr)
    salvar('Personagens', 'pai', P.sprite_pai())

    # ---------------- retratos
    for nome, fn in P.EMOCOES:
        salvar('Retratos', 'joaquim_' + fn.__name__, P.retrato_joaquim(fn))
    salvar('Retratos', 'pai_normal', P.retrato_pai(P.pai_normal))
    salvar('Retratos', 'pai_feliz', P.retrato_pai(P.pai_feliz))
    salvar('Retratos', 'relogio', O.relogio_retrato())

    # ---------------- cenários
    for nome, rows in mapas.items():
        print('chão', nome, len(rows[0]), 'x', len(rows))
        salvar('Cenarios', nome.lower() + '_chao', C.chao(nome, rows))
    esc = mapas['Escola']
    linha_fachada = next(r for r in esc if 'D' in r)
    salvar('Cenarios', 'escola_fachada', C.fachada_escola(linha_fachada))
    salvar('Cenarios', 'escola_telhado', C.telhado(len(esc[0])))
    salvar('Cenarios', 'escola_ceu', C.ceu('4a5a9a', 'e8977a', 'ffd99a'))
    salvar('Cenarios', 'floresta_ceu', C.ceu('0e2a2a', '2a5a4a', '8ab890'))
    for nome in ('Casa', 'Quarto'):
        rows = mapas[nome]
        salvar('Cenarios', nome.lower() + '_parede', C.parede(rows[0]))
        salvar('Cenarios', nome.lower() + '_parede_lado', C.parede_lado(len(rows)))
    salvar('Cenarios', 'porta', C.porta(False))
    salvar('Cenarios', 'porta_aberta', C.porta(True))

    # ---------------- objetos
    for i in range(4):
        salvar('Objetos', f'arvore{i}', O.arvore(s=3 + i * 7))
        salvar('Objetos', f'arvore_mata{i}', O.arvore_mata(s=40 + i * 5))
    for i in range(2):
        salvar('Objetos', f'arbusto{i}', O.arbusto(s=4 + i * 9))
        salvar('Objetos', f'capim{i}', O.capim(i + 1))
    salvar('Objetos', 'cerca', O.cerca())
    salvar('Objetos', 'poste', O.poste())
    salvar('Objetos', 'poltrona', O.poltrona())
    salvar('Objetos', 'mesinha', O.mesinha())
    salvar('Objetos', 'tv', O.tv())
    salvar('Objetos', 'planta', O.planta())
    salvar('Objetos', 'cama_topo', O.cama_topo(False))
    salvar('Objetos', 'cama_topo_dormindo', O.cama_topo(True))
    salvar('Objetos', 'cama_frente', O.cama_frente())
    salvar('Objetos', 'cama_cabeceira', O.cama_cabeceira())
    salvar('Objetos', 'cogumelo', O.cogumelo())
    salvar('Objetos', 'tronco', O.tronco())
    salvar('Objetos', 'brilho0', O.brilho(False))
    salvar('Objetos', 'brilho1', O.brilho(True))
    salvar('Objetos', 'exclamacao', O.exclamacao())

    # ---------------- efeitos (filtro suave, ver ArtImporter.cs)
    salvar('Efeitos', 'sombra', O.sombra())
    salvar('Efeitos', 'luz', O.luz())
    salvar('Efeitos', 'pontinho', O.pontinho())
    print('arte gerada em', SAIDA)


if __name__ == '__main__':
    main()
