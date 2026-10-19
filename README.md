# Joaquim No Reino da Fantasia

Jogo pixelado para celular (Android e iPhone) feito na **Unity 6.3 LTS** com C#.
Este repositório tem o **Capítulo 1 (prólogo)**:

1. Joaquim sai da escola e acha, perto do gramado, um relógio de pulso que brilha.
2. Em casa, conversa com o pai e vai para o quarto.
3. Ao deitar, o relógio emite uma luz que cresce até tomar o quarto inteiro.
4. Ele abre os olhos numa floresta densa... *continua.*

Visual **HD-2D** (inspirado em Octopath Traveler): pixel art dentro de cenários 3D com
câmera em perspectiva, desfoque de profundidade, brilho (bloom), raios de luz, névoa e
partículas. Os mapas são desenhados com caracteres e os sons são sintetizados.

## Download para testar

- iPhone (SideStore): https://github.com/2d87h5jcdz-hub/Aventuras-no-mundo-da-fantasia-/releases/latest/download/Joaquim.ipa
- Android: https://github.com/2d87h5jcdz-hub/Aventuras-no-mundo-da-fantasia-/releases/latest/download/Joaquim.apk

## Vídeo de abertura

`Assets/StreamingAssets/abertura.mp4` (2:19, com música) toca ao abrir o jogo; um toque pula.
É gerado pelos scripts em `tools/abertura` — veja `tools/abertura/LEIAME.md`.

## Arte

Toda a arte é gerada pelo script `tools/arte/gerar.py` (Python + numpy + Pillow) e salva em
`Assets/Resources/Art`. Para mudar algo visual, edite o script e rode de novo:

```
pip install numpy pillow
python tools/arte/gerar.py
```

| Pasta | Conteúdo |
|---|---|
| `Personagens/` | Joaquim (4 direções + passo, deitado) e o pai |
| `Retratos/` | retratos 48x48 com emoções (normal, feliz, animado, surpreso, triste, chateado, raiva, medo) |
| `Cenarios/` | chão de cada mapa, fachada, telhado, paredes, portas, céu |
| `Objetos/` | árvores, arbustos, cerca, poste, móveis, coisas da floresta |
| `Efeitos/` | sombra, luz e partículas (filtro suave) |

## Rodar no computador (Windows)

1. Instale o **Unity Hub** e, por ele, a **Unity 6.3 LTS** (versão mais recente da 6.3).
   Marque os módulos *Android Build Support* (para testar no celular pelo cabo) e,
   se quiser, *iOS Build Support*.
2. No Hub: **Add → Add project from disk** e escolha esta pasta.
   Se o Hub disser que a versão é diferente, aceite abrir com a sua 6.3 e
   **faça commit do `ProjectSettings/ProjectVersion.txt` atualizado**, para o GitHub Actions usar a mesma versão.
3. Na primeira abertura, a cena `Assets/Scenes/Main.unity` é criada automaticamente.
   Se o Unity perguntar sobre o *Input System* e pedir para reiniciar, pode aceitar.
4. Aperte **Play**.

Controles: **setas/WASD** para andar, **Espaço/Enter** para interagir/avançar.
No celular: encoste o dedo na **metade esquerda** da tela e arraste — um joystick aparece ali e some ao soltar.
Toque na **metade direita** para interagir (em alguém/algo, ou com o que estiver na frente) e para avançar o texto.

## Build automático no GitHub Actions (APK + IPA)

O workflow `.github/workflows/build.yml` roda a cada push na `main` (ou manualmente em *Actions → Run workflow*):

- **Job Linux (GameCI):** gera o `Joaquim.apk` e o projeto Xcode.
- **Job macOS:** compila o projeto Xcode sem assinatura e gera o `Joaquim.ipa`
  (para instalar com o SideStore, como no Pestana Estúdio).

Os arquivos aparecem em **Actions → (execução) → Artifacts**: `Joaquim-Android-apk` e `Joaquim-iOS-ipa`.

### Configuração única: licença da Unity

Em **Settings → Secrets and variables → Actions → New repository secret**, crie:

| Secret | Valor |
|---|---|
| `UNITY_EMAIL` | e-mail da sua conta Unity |
| `UNITY_PASSWORD` | senha da conta Unity |
| `UNITY_LICENSE` | conteúdo inteiro do arquivo `C:\ProgramData\Unity\Unity_lic.ulf` |

O arquivo `.ulf` aparece depois de ativar a licença **Personal** (gratuita) no Unity Hub
(*Preferences → Licenses → Add*). A pasta `ProgramData` é oculta no Explorer.

O primeiro build demora mais (baixa a imagem da Unity e importa tudo);
os seguintes usam cache da pasta `Library`.

## Onde mexer

| Quero mudar... | Arquivo |
|---|---|
| Falas, textos e emoções dos retratos | `Assets/Scripts/Story/Roteiro.cs` |
| Clima visual de cada lugar (câmera, luz, desfoque, cor) | `Assets/Scripts/Render/ScenePreset.cs` |
| Como cada mapa vira cenário 3D | `Assets/Scripts/World/SceneBuilder.cs` |
| Ordem dos acontecimentos (cenas) | `Assets/Scripts/Story/StoryDirector.cs` |
| Cenários (mapas em texto) | `Assets/Scripts/World/Maps.cs` |
| Quais caracteres do mapa bloqueiam a passagem | `Assets/Scripts/World/TileLegend.cs` |
| Desenhos (pixel art) | `tools/arte/*.py` → `Assets/Resources/Art` |
| Nome do app, ID, orientação | `Assets/Editor/BuildScript.cs` |

### Estrutura

```
Assets/
  Scripts/
    GameBootstrap.cs      monta câmera, mundo, personagem e história ao dar Play
    Render/               visual HD-2D: quads 3D, shaders, pós-processamento, partículas
    World/                mapas, montagem 3D, colisão, gatilhos, caminho (toque pra andar)
    Actors/               Joaquim (movimento em grade) e animação de quadros
    UI/                   caixa de diálogo, fades, letreiros (IMGUI)
    Story/                roteiro (texto) e diretor (sequência das cenas)
    Audio/                efeitos 8 bits gerados por código
    Core/                 entrada (toque/teclado) e câmera em perspectiva
  Resources/Art/          imagens geradas por tools/arte/gerar.py
  Resources/Shaders/      shaders do visual HD-2D
  Editor/BuildScript.cs   build usado pelo CI e menu "Joaquim" no editor
```
