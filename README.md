# Joaquim e o Relógio de Luz

Jogo pixelado para celular (Android e iPhone) feito na **Unity 6.3 LTS** com C#.
Este repositório tem o **Capítulo 1 (prólogo)**:

1. Joaquim sai da escola e acha, perto do gramado, um relógio de pulso que brilha.
2. Em casa, conversa com o pai e vai para o quarto.
3. Ao deitar, o relógio emite uma luz que cresce até tomar o quarto inteiro.
4. Ele abre os olhos numa floresta densa... *continua.*

Tudo é montado por código: a arte é desenhada em texto (pixel por pixel), os mapas são
desenhados com caracteres e os sons são sintetizados. Não há arquivos de imagem ou áudio.

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
No celular: **toque** onde quer ir; toque em alguém ou na cama para interagir; toque para avançar o texto.

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
| Falas e textos das telas | `Assets/Scripts/Story/Roteiro.cs` |
| Ordem dos acontecimentos (cenas) | `Assets/Scripts/Story/StoryDirector.cs` |
| Cenários (mapas em texto) | `Assets/Scripts/World/Maps.cs` |
| O que cada caractere do mapa significa | `Assets/Scripts/World/TileLegend.cs` |
| Desenhos (pixel art 16×16) e paleta | `Assets/Scripts/Art/PixelArtData.cs` |
| Nome do app, ID, orientação | `Assets/Editor/BuildScript.cs` |

### Estrutura

```
Assets/
  Scripts/
    GameBootstrap.cs      monta câmera, mundo, personagem e história ao dar Play
    Art/                  pixel art em texto + conversão para Sprites
    World/                mapas, tiles, colisão, gatilhos, caminho (toque pra andar)
    Actors/               Joaquim (movimento em grade) e animação de quadros
    UI/                   caixa de diálogo, fades, letreiros (IMGUI)
    Story/                roteiro (texto) e diretor (sequência das cenas)
    Audio/                efeitos 8 bits gerados por código
    Core/                 entrada (toque/teclado) e câmera pixel perfect
  Editor/BuildScript.cs   build usado pelo CI e menu "Joaquim" no editor
```
