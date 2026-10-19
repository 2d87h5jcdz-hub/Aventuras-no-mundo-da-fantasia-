using System.Collections;
using System.Collections.Generic;
using Joaquim.Actors;
using Joaquim.Audio;
using Joaquim.Core;
using Joaquim.Render;
using Joaquim.UI;
using Joaquim.World;
using UnityEngine;

namespace Joaquim.Story
{
    /// <summary>
    /// O "diretor" da história: carrega cada cenário, coloca personagens e gatilhos,
    /// e roda as cenas (cutscenes) na ordem certa.
    /// As falas ficam em Roteiro.cs; aqui fica só o "quando" e o "como".
    /// </summary>
    public sealed class StoryDirector : MonoBehaviour
    {
        GameWorld _world;
        Player _player;
        CameraRig _rig;
        DialogueBox _dialogue;
        ScreenFader _fader;
        Motes _motes;
        IntroVideo _intro;
        bool _introPlayed;

        // Estado da história
        bool _busy, _restart;
        bool _noticedGlint, _hasWatch, _talkedToPai;
        Vector2Int _watchCell, _doorCell, _bedHeadCell;
        Quad _glint;

        public void Init(GameWorld world, Player player, CameraRig rig, DialogueBox dialogue, ScreenFader fader, Motes motes,
            IntroVideo intro)
        {
            _intro = intro;
            _motes = motes;
            _world = world;
            _player = player;
            _rig = rig;
            _dialogue = dialogue;
            _fader = fader;
            _player.CellEntered += OnPlayerEnteredCell;
        }

        void Start() => StartCoroutine(Run());

        // ================================================================ abertura

        IEnumerator Run()
        {
            _busy = true;
            _noticedGlint = _hasWatch = _talkedToPai = false;

            _fader.Set(Color.black, 1f);
            _fader.Vignette = false;
            LoadMap(Maps.Escola);
            _player.Locked = true;
            yield return null;

            // vídeo de abertura (só na primeira vez; ao jogar de novo vai direto ao título)
            if (!_introPlayed && _intro != null)
            {
                _introPlayed = true;
                yield return _intro.Play();
            }

            // Tela de título com a escola ao fundo
            yield return _fader.FadeTo(Color.black, 0.6f, 1f);
            _fader.ShowCaption(Roteiro.Titulo, Roteiro.TocarParaComecar, blinkSubtitle: true);
            yield return WaitTap();
            Sfx.Chime();
            _fader.HideCaption();
            yield return _fader.FadeTo(Color.black, 1f, 0.5f);

            _fader.ShowCaption(Roteiro.Capitulo1, Roteiro.Capitulo1Nome);
            yield return new WaitForSeconds(2.2f);
            yield return _fader.FadeCaption(0f, 0.6f);
            yield return _fader.FadeTo(Color.black, 0f, 1.2f);

            yield return Say(Roteiro.EscolaInicio);
            _player.Locked = false;
            _busy = false;
        }

        // ================================================================ montagem dos mapas

        void LoadMap(MapDef map)
        {
            _world.Load(map);
            var spawn = _world.FindAll('@');
            _player.Place(spawn.Count > 0 ? spawn[0] : Vector2Int.zero);
            _player.SetVisible(true);
            _player.SetLying(false);
            _rig.Shake = 0f;
            _rig.Snap();
            _motes.Configure(_world.Preset.MoteCount, _world.Preset.MoteColor, _world.Preset.MoteSize);

            if (map == Maps.Escola) SetupEscola();
            else if (map == Maps.Casa) SetupCasa();
            else if (map == Maps.Quarto) SetupQuarto();
            else if (map == Maps.Floresta) SetupFloresta();
        }

        void SetupEscola()
        {
            _watchCell = _world.FindAll('*')[0];
            _glint = _world.SpawnBillboard("Brilho", Art.Tex("Objetos/brilho0"), _watchCell, QuadStyle.Additive, 1f, 0.05f);
            _glint.SetColor(new Color(1f, 1f, 1f, 1.4f));
            _glint.gameObject.AddComponent<FrameAnimator>().Play(
                new[] { Art.Tex("Objetos/brilho0"), Art.Tex("Objetos/brilho1"), Art.Tex("Objetos/brilho0"), null },
                new[] { 0.15f, 0.25f, 0.15f, 1.1f });

            _world.OnStep(_watchCell, () => Trigger(AchouRelogio()));
            foreach (var exit in _world.FindAll('X'))
                _world.OnStep(exit, () => Trigger(SaidaEscola()));
        }

        void SetupCasa()
        {
            var pai = _world.FindAll('P')[0];
            _world.SpawnBillboard("Pai", Art.Tex("Personagens/pai"), pai);
            _world.SpawnShadow(GameWorld.CellToWorld(pai), 0.55f);
            _world.AddBlocker(pai);
            _world.OnInteract(pai, () => Trigger(ConversaPai()), 2.4f);

            _doorCell = _world.FindAll('d')[0];
            _world.OnStep(_doorCell, () => Trigger(PortaQuarto()));
        }

        void SetupQuarto()
        {
            _bedHeadCell = _world.FindAll('B')[0];
            _world.OnInteract(_bedHeadCell, () => Trigger(Dormir()), 1.4f);
            foreach (var foot in _world.FindAll('E'))
                _world.OnInteract(foot, () => Trigger(Dormir()), 0.6f);
        }

        void SetupFloresta()
        {
            foreach (var end in _world.FindAll('!'))
                _world.OnStep(end, () => Trigger(FimDoCapitulo()));
        }

        void OnPlayerEnteredCell(Vector2Int cell)
        {
            if (_world.Map != Maps.Escola || _hasWatch || _noticedGlint) return;
            if (cell == _watchCell) return; // pisou direto no relógio: a cena de achar já cuida
            int dist = Mathf.Max(Mathf.Abs(cell.x - _watchCell.x), Mathf.Abs(cell.y - _watchCell.y));
            if (dist <= 3) Trigger(ViuBrilho());
        }

        // ================================================================ cenas

        IEnumerator ViuBrilho()
        {
            _noticedGlint = true;
            yield return Exclaim();
            yield return Say(Roteiro.ViuBrilho);
        }

        IEnumerator AchouRelogio()
        {
            _noticedGlint = true;
            _world.ClearStep(_watchCell);
            if (_glint != null) Destroy(_glint.gameObject);
            Sfx.Chime();
            yield return Exclaim();
            yield return Say(Roteiro.AchouRelogio);
            _hasWatch = true;
        }

        IEnumerator SaidaEscola()
        {
            if (!_hasWatch)
            {
                yield return Say(Roteiro.SaidaSemRelogio);
                yield return _player.ScriptedStep(new Vector2Int(0, -1));
                yield break;
            }

            yield return _fader.FadeTo(Color.black, 1f, 0.8f);
            _fader.ShowCaption(Roteiro.LegendaCasa);
            LoadMap(Maps.Casa);
            _player.FaceTo(Player.Facing.Up);
            yield return new WaitForSeconds(1.4f);
            yield return _fader.FadeCaption(0f, 0.5f);
            yield return _fader.FadeTo(Color.black, 0f, 0.8f);
        }

        IEnumerator ConversaPai()
        {
            if (_talkedToPai)
            {
                yield return Say(Roteiro.PaiDepois);
                yield break;
            }
            yield return Say(Roteiro.ConversaPai);
            _talkedToPai = true;
            if (_world.Door != null) _world.Door.SetTexture(Art.Tex("Cenarios/porta_aberta"));
            Sfx.Door();
        }

        IEnumerator PortaQuarto()
        {
            if (!_talkedToPai)
            {
                yield return Say(Roteiro.PortaAntesDoPai);
                yield return _player.ScriptedStep(new Vector2Int(0, 1));
                yield break;
            }

            Sfx.Door();
            yield return _fader.FadeTo(Color.black, 1f, 0.8f);
            _fader.ShowCaption(Roteiro.LegendaNoite);
            LoadMap(Maps.Quarto);
            yield return new WaitForSeconds(1.4f);
            yield return _fader.FadeCaption(0f, 0.5f);
            yield return _fader.FadeTo(Color.black, 0f, 0.8f);
            yield return Say(Roteiro.QuartoChegada);
        }

        IEnumerator Dormir()
        {
            // Joaquim deita
            yield return _fader.FadeTo(Color.black, 1f, 0.6f);
            _player.SetVisible(false);
            if (_world.BedTop != null) _world.BedTop.SetTexture(Art.Tex("Objetos/cama_topo_dormindo"));
            yield return new WaitForSeconds(0.4f);
            yield return _fader.FadeTo(Color.black, 0.35f, 1f);
            yield return Say(Roteiro.NaCama);

            // tic... tac... pequenas piscadas de luz saindo do pulso
            var center = GameWorld.CellToWorld(_bedHeadCell) + new Vector3(0f, 0.75f, -0.6f);
            var glow = Quad.Surface("Luz do relógio", _world.Root, Art.Tex("Efeitos/luz"),
                new Vector3(-0.5f, 0.5f, 0f), Vector3.right, Vector3.down, QuadStyle.Additive);
            glow.transform.position = center;
            glow.SetColor(new Color(0.7f, 1f, 1f, 1.6f));
            var floor = _world.SpawnLight(center, 0.5f, new Color(0.55f, 0.95f, 1f, 0.9f));
            for (int i = 0; i < 4; i++)
            {
                Sfx.Tick();
                glow.transform.localScale = Vector3.one * (0.5f + i * 0.2f);
                glow.Visible = floor.Visible = true;
                yield return new WaitForSeconds(0.12f);
                glow.Visible = floor.Visible = false;
                yield return new WaitForSeconds(0.55f);
            }
            glow.Visible = floor.Visible = true;
            glow.transform.localScale = Vector3.one * 0.8f;
            yield return _fader.FadeTo(Color.black, 0f, 0.4f);
            yield return Say(Roteiro.RelogioBrilha);

            // a luz cresce até tomar o quarto inteiro
            Sfx.Hum();
            const float duration = 4.5f;
            bool whiteStarted = false;
            for (float t = 0; t < duration; t += Time.deltaTime)
            {
                float k = t / duration;
                float pulse = 1f + Mathf.Sin(t * Mathf.Lerp(6f, 22f, k)) * 0.08f;
                float size = Mathf.Lerp(0.8f, 26f, k * k * k) * pulse;
                glow.transform.localScale = Vector3.one * size;
                floor.transform.localScale = new Vector3(size, 1f, size);
                _rig.Shake = Mathf.Lerp(0f, 0.15f, k);
                if (!whiteStarted && k > 0.55f)
                {
                    whiteStarted = true;
                    StartCoroutine(_fader.FadeTo(Color.white, 1f, duration * 0.42f));
                }
                yield return null;
            }
            _fader.Set(Color.white, 1f);
            _rig.Shake = 0f;
            yield return new WaitForSeconds(1.2f);

            // ...e ele acorda em outro lugar
            LoadMap(Maps.Floresta);
            _player.SetLying(true);
            yield return new WaitForSeconds(0.5f);
            yield return _fader.FadeTo(Color.white, 0f, 2.8f);
            yield return Say(Roteiro.Acordou);

            _player.SetLying(false);
            _player.FaceTo(Player.Facing.Down);
            yield return new WaitForSeconds(0.3f);
            _player.FaceTo(Player.Facing.Left);
            yield return new WaitForSeconds(0.45f);
            _player.FaceTo(Player.Facing.Right);
            yield return new WaitForSeconds(0.45f);
            _player.FaceTo(Player.Facing.Down);
            yield return Say(Roteiro.Levantou);
        }

        IEnumerator FimDoCapitulo()
        {
            yield return Say(Roteiro.FimCapitulo);
            yield return _fader.FadeTo(Color.black, 1f, 1.5f);
            _fader.Vignette = false;
            _fader.ShowCaption(Roteiro.FimTitulo, Roteiro.FimSubtitulo);
            yield return new WaitForSeconds(2.5f);
            _fader.ShowCaption(Roteiro.FimTitulo, Roteiro.JogarDeNovo, blinkSubtitle: true);
            yield return WaitTap();
            _fader.HideCaption();
            _restart = true;
        }

        // ================================================================ utilidades

        /// <summary>Roda uma cena travando o controle do jogador; ignora se já tem outra rodando.</summary>
        void Trigger(IEnumerator scene)
        {
            if (_busy) return;
            StartCoroutine(RunScene(scene));
        }

        IEnumerator RunScene(IEnumerator scene)
        {
            _busy = true;
            _player.Locked = true;
            yield return StartCoroutine(scene);
            if (_restart)
            {
                _restart = false;
                StartCoroutine(Run()); // Run cuida de travar/destravar
                yield break;
            }
            _player.Locked = false;
            _busy = false;
        }

        IEnumerator Say(IEnumerable<Fala> falas)
        {
            foreach (var f in falas)
                yield return _dialogue.Say(NomeDe(f.Quem), f.Texto, RetratoDe(f));
        }

        static string NomeDe(Quem q)
        {
            switch (q)
            {
                case Quem.Joaquim: return "Joaquim";
                case Quem.Pai: return "Pai";
                default: return null; // narração
            }
        }

        static Texture2D RetratoDe(Fala f)
        {
            if (f.MostraRelogio) return Art.Tex("Retratos/relogio");
            switch (f.Quem)
            {
                case Quem.Joaquim:
                    return Art.Tex("Retratos/joaquim_" + f.Emocao.ToString().ToLowerInvariant());
                case Quem.Pai:
                    bool alegre = f.Emocao == Emocao.Feliz || f.Emocao == Emocao.Animado;
                    return Art.Tex(alegre ? "Retratos/pai_feliz" : "Retratos/pai_normal");
                default:
                    return null;
            }
        }

        /// <summary>Balãozinho de "!" em cima do Joaquim.</summary>
        IEnumerator Exclaim()
        {
            var basePos = _player.transform.position + new Vector3(0f, 2.25f, -0.05f);
            var bubble = Quad.Billboard("!", _world.Root, Art.Tex("Objetos/exclamacao"), basePos);
            for (float t = 0; t < 0.7f; t += Time.deltaTime)
            {
                float hop = t < 0.15f ? Mathf.Sin(t / 0.15f * Mathf.PI) * 0.25f : 0f;
                bubble.transform.position = basePos + new Vector3(0f, hop, 0f);
                yield return null;
            }
            Destroy(bubble.gameObject);
        }

        static IEnumerator WaitTap()
        {
            yield return null; // não aproveita o toque do frame anterior
            while (!InputBridge.AnyConfirm()) yield return null;
            InputBridge.Consume();
        }
    }
}
