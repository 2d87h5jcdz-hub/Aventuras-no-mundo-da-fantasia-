using System.Collections;
using System.Collections.Generic;
using Joaquim.Actors;
using Joaquim.Art;
using Joaquim.Audio;
using Joaquim.Core;
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

        // Estado da história
        bool _busy, _restart;
        bool _noticedGlint, _hasWatch, _talkedToPai;
        Vector2Int _watchCell, _doorCell, _bedHeadCell;
        SpriteRenderer _glint;

        public void Init(GameWorld world, Player player, CameraRig rig, DialogueBox dialogue, ScreenFader fader)
        {
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

            if (map == Maps.Escola) SetupEscola();
            else if (map == Maps.Casa) SetupCasa();
            else if (map == Maps.Quarto) SetupQuarto();
            else if (map == Maps.Floresta) SetupFloresta();
        }

        void SetupEscola()
        {
            _watchCell = _world.FindAll('*')[0];
            _glint = _world.SpawnSprite("Brilho", PixelArtData.Glint0, _watchCell, GameWorld.OrderItems);
            _glint.gameObject.AddComponent<FrameAnimator>().Play(
                new[] { PixelArtData.Glint0, PixelArtData.Glint1, PixelArtData.Glint0, null },
                new[] { 0.15f, 0.25f, 0.15f, 1.1f });

            _world.OnStep(_watchCell, () => Trigger(AchouRelogio()));
            foreach (var exit in _world.FindAll('X'))
                _world.OnStep(exit, () => Trigger(SaidaEscola()));
        }

        void SetupCasa()
        {
            var pai = _world.FindAll('P')[0];
            _world.SpawnSprite("Pai", PixelArtData.Pai, pai, GameWorld.OrderActors);
            _world.AddBlocker(pai);
            _world.OnInteract(pai, () => Trigger(ConversaPai()));

            _doorCell = _world.FindAll('d')[0];
            _world.OnStep(_doorCell, () => Trigger(PortaQuarto()));
        }

        void SetupQuarto()
        {
            _bedHeadCell = _world.FindAll('B')[0];
            _world.OnInteract(_bedHeadCell, () => Trigger(Dormir()));
            foreach (var foot in _world.FindAll('E'))
                _world.OnInteract(foot, () => Trigger(Dormir()));
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
            _world.SetTileArt(_doorCell, PixelArtData.DoorOpen);
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
            // o quarto fica à meia-luz: é noite
            yield return _fader.FadeTo(Color.black, 0.25f, 0.8f);
            yield return Say(Roteiro.QuartoChegada);
        }

        IEnumerator Dormir()
        {
            // Joaquim deita
            yield return _fader.FadeTo(Color.black, 1f, 0.6f);
            _player.SetVisible(false);
            _world.SetTileArt(_bedHeadCell, PixelArtData.BedSleeping);
            yield return new WaitForSeconds(0.4f);
            yield return _fader.FadeTo(Color.black, 0.5f, 1f);
            yield return Say(Roteiro.NaCama);

            // tic... tac... pequenas piscadas de luz
            var glow = _world.SpawnSprite("Luz do relógio", null, _bedHeadCell, GameWorld.OrderEffects);
            glow.sprite = SpriteFactory.Glow();
            for (int i = 0; i < 4; i++)
            {
                Sfx.Tick();
                glow.transform.localScale = Vector3.one * (0.18f + i * 0.06f);
                glow.enabled = true;
                yield return new WaitForSeconds(0.12f);
                glow.enabled = false;
                yield return new WaitForSeconds(0.55f);
            }
            glow.enabled = true;
            glow.transform.localScale = Vector3.one * 0.3f;
            yield return Say(Roteiro.RelogioBrilha);

            // a luz cresce até tomar o quarto inteiro
            Sfx.Hum();
            const float duration = 4.5f;
            bool whiteStarted = false;
            for (float t = 0; t < duration; t += Time.deltaTime)
            {
                float k = t / duration;
                float pulse = 1f + Mathf.Sin(t * Mathf.Lerp(6f, 22f, k)) * 0.08f;
                glow.transform.localScale = Vector3.one * Mathf.Lerp(0.3f, 12f, k * k * k) * pulse;
                _rig.Shake = Mathf.Lerp(0f, 0.12f, k);
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
            _fader.Vignette = true;
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

        static Sprite RetratoDe(Fala f)
        {
            if (f.MostraRelogio) return SpriteFactory.Get(PixelArtData.Watch);
            switch (f.Quem)
            {
                case Quem.Joaquim: return SpriteFactory.Get(PixelArtData.JoaquimDown0);
                case Quem.Pai: return SpriteFactory.Get(PixelArtData.Pai);
                default: return null;
            }
        }

        /// <summary>Balãozinho de "!" em cima do Joaquim.</summary>
        IEnumerator Exclaim()
        {
            var bubble = _world.SpawnSprite("!", PixelArtData.Exclaim, _player.Cell, GameWorld.OrderEffects);
            var basePos = _player.transform.position + new Vector3(0f, 0.85f, 0f);
            for (float t = 0; t < 0.7f; t += Time.deltaTime)
            {
                float hop = t < 0.15f ? Mathf.Sin(t / 0.15f * Mathf.PI) * 0.2f : 0f;
                var p = basePos + new Vector3(0f, hop, 0f);
                p.y = Mathf.Round(p.y * SpriteFactory.PixelsPerUnit) / SpriteFactory.PixelsPerUnit;
                bubble.transform.position = p;
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
