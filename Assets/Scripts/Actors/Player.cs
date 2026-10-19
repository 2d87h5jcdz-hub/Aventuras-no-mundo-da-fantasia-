using System;
using System.Collections;
using System.Collections.Generic;
using Joaquim.Core;
using Joaquim.Render;
using Joaquim.UI;
using Joaquim.World;
using UnityEngine;

namespace Joaquim.Actors
{
    /// <summary>
    /// O Joaquim. Anda de tile em tile, como nos RPGs clássicos.
    /// No celular: toque num lugar para ir até lá; toque em alguém/algo para interagir.
    /// No computador: setas/WASD para andar, Espaço/Enter para interagir.
    /// </summary>
    public sealed class Player : MonoBehaviour
    {
        public enum Facing { Down, Up, Left, Right }

        public GameWorld World;
        public Camera Cam;

        /// <summary>Enquanto a história está contando algo, o jogador não controla o Joaquim.</summary>
        public bool Locked;

        public Vector2Int Cell { get; private set; }
        public Facing Face { get; private set; } = Facing.Down;
        public bool IsMoving => _moving;

        /// <summary>Disparado sempre que o Joaquim termina de entrar numa célula.</summary>
        public event Action<Vector2Int> CellEntered;

        const float StepTime = 0.2f;

        Quad _body;
        Quad _shadow;
        readonly Queue<Vector2Int> _path = new Queue<Vector2Int>();
        Vector2Int? _pendingInteract;
        bool _moving, _scripted, _lying, _visible = true;
        Vector3 _from, _to;
        float _t;
        int _steps;

        static Texture2D T(string n) => Art.Tex("Personagens/joaquim_" + n);

        void Awake()
        {
            _body = Quad.Billboard("sprite", transform, T("baixo0"), Vector3.zero);
            _body.transform.localPosition = Vector3.zero;
        }

        /// <summary>Chamado depois de trocar de mapa: refaz a sombra com a luz do novo lugar.</summary>
        public void Place(Vector2Int cell, Facing face = Facing.Down)
        {
            Cell = cell;
            Face = face;
            _moving = false;
            _path.Clear();
            _pendingInteract = null;
            transform.position = GameWorld.CellToWorld(cell);
            if (_shadow != null) Destroy(_shadow.gameObject);
            _shadow = World.SpawnShadow(transform.position, 0.5f, transform);
            _body.SetColor(World.Preset.PropTint);
            ApplyVisibility();
            UpdateSprite();
        }

        public void SetVisible(bool visible)
        {
            _visible = visible;
            ApplyVisibility();
        }

        void ApplyVisibility()
        {
            _body.Visible = _visible;
            if (_shadow != null) _shadow.Visible = _visible && !_lying;
        }

        public void SetLying(bool lying)
        {
            _lying = lying;
            ApplyVisibility();
            UpdateSprite();
        }

        public void FaceTo(Facing face)
        {
            Face = face;
            UpdateSprite();
        }

        /// <summary>Passo controlado pela história (ex.: dar um passo pra trás). Não dispara gatilhos.</summary>
        public IEnumerator ScriptedStep(Vector2Int delta)
        {
            var target = Cell + delta;
            Face = FacingFrom(delta);
            if (!World.IsWalkable(target)) { UpdateSprite(); yield break; }
            _scripted = true;
            BeginStep(target);
            while (_moving) yield return null;
            _scripted = false;
        }

        void Update()
        {
            if (_moving)
            {
                Advance();
                return;
            }

            if (Locked || DialogueBox.IsOpen)
            {
                _path.Clear();
                _pendingInteract = null;
                return;
            }

            // Teclado
            var held = InputBridge.HeldDirection();
            if (held != Vector2Int.zero)
            {
                _path.Clear();
                _pendingInteract = null;
                TryWalk(new Vector2Int(held.x, -held.y)); // tela: cima = y menor no mapa
                return;
            }

            if (InputBridge.ActionKeyPressed())
            {
                World.TryInteract(Cell + DeltaOf(Face));
                return;
            }

            // Toque / clique
            if (InputBridge.PointerPressed(out var screen))
                HandleTap(screen);

            if (_path.Count > 0)
            {
                var next = _path.Dequeue();
                if (World.IsWalkable(next) && GameWorld.AreNeighbors(Cell, next))
                    BeginStep(next);
                else
                {
                    _path.Clear();
                    _pendingInteract = null;
                }
            }
            else if (_pendingInteract.HasValue)
            {
                var target = _pendingInteract.Value;
                _pendingInteract = null;
                if (GameWorld.AreNeighbors(Cell, target))
                {
                    FaceTo(FacingFrom(target - Cell));
                    World.TryInteract(target);
                }
            }
        }

        void TryWalk(Vector2Int delta)
        {
            Face = FacingFrom(delta);
            var target = Cell + delta;
            if (World.IsWalkable(target))
                BeginStep(target);
            else
            {
                UpdateSprite();
                World.TryInteract(target); // "esbarrar" em algo também interage
            }
        }

        void HandleTap(Vector2 screen)
        {
            if (Cam == null) return;
            var ray = Cam.ScreenPointToRay(new Vector3(screen.x, screen.y, 0f));

            _path.Clear();
            _pendingInteract = null;

            Vector2Int target;
            if (!World.PickInteraction(ray, out target))
            {
                if (!GameWorld.PickGround(ray, out target)) return;
            }
            if (target == Cell) return;

            if (World.HasInteraction(target) && !World.IsWalkable(target))
            {
                if (GameWorld.AreNeighbors(Cell, target))
                {
                    FaceTo(FacingFrom(target - Cell));
                    World.TryInteract(target);
                    return;
                }
                var path = World.FindPath(Cell, c => GameWorld.AreNeighbors(c, target));
                if (path == null) return;
                foreach (var c in path) _path.Enqueue(c);
                _pendingInteract = target;
                return;
            }

            if (World.IsWalkable(target))
            {
                var path = World.FindPath(Cell, c => c == target);
                if (path == null) return;
                foreach (var c in path) _path.Enqueue(c);
            }
        }

        void BeginStep(Vector2Int target)
        {
            Face = FacingFrom(target - Cell);
            _from = GameWorld.CellToWorld(Cell);
            _to = GameWorld.CellToWorld(target);
            Cell = target;
            _t = 0f;
            _moving = true;
            _steps++;
            UpdateSprite();
        }

        void Advance()
        {
            _t += Time.deltaTime / StepTime;
            if (_t >= 1f)
            {
                _moving = false;
                transform.position = _to;
                UpdateSprite();
                if (_scripted) return;

                CellEntered?.Invoke(Cell);
                World.TryStep(Cell);
                if (Locked)
                {
                    _path.Clear();
                    _pendingInteract = null;
                }
                return;
            }

            transform.position = Vector3.Lerp(_from, _to, _t);
            UpdateSprite();
        }

        void UpdateSprite()
        {
            if (_body == null) return;
            if (_lying)
            {
                _body.SetTexture(T("deitado"));
                _body.SetFlip(false);
                return;
            }

            bool stride = _moving && _t < 0.5f; // metade do passo com a perna levantada
            switch (Face)
            {
                case Facing.Down:
                    _body.SetTexture(T(stride ? "baixo1" : "baixo0"));
                    _body.SetFlip(stride && _steps % 2 == 0);
                    break;
                case Facing.Up:
                    _body.SetTexture(T(stride ? "cima1" : "cima0"));
                    _body.SetFlip(stride && _steps % 2 == 0);
                    break;
                case Facing.Left:
                case Facing.Right:
                    _body.SetTexture(T(stride ? "lado1" : "lado0"));
                    _body.SetFlip(Face == Facing.Left);
                    break;
            }
        }

        public static Facing FacingFrom(Vector2Int delta)
        {
            if (delta.x > 0) return Facing.Right;
            if (delta.x < 0) return Facing.Left;
            return delta.y < 0 ? Facing.Up : Facing.Down;
        }

        public static Vector2Int DeltaOf(Facing f)
        {
            switch (f)
            {
                case Facing.Up: return new Vector2Int(0, -1);
                case Facing.Left: return new Vector2Int(-1, 0);
                case Facing.Right: return new Vector2Int(1, 0);
                default: return new Vector2Int(0, 1);
            }
        }
    }
}
