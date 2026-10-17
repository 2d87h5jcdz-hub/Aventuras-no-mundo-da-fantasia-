using System;
using System.Collections.Generic;
using Joaquim.Art;
using UnityEngine;

namespace Joaquim.World
{
    /// <summary>
    /// Monta o mapa atual na tela e responde perguntas sobre ele:
    /// dá pra andar aqui? tem gatilho? tem algo pra interagir?
    /// Coordenadas: célula (x, y) com y crescendo pra baixo; no mundo vira (x, -y).
    /// </summary>
    public sealed class GameWorld : MonoBehaviour
    {
        public const int OrderGround = 0;
        public const int OrderItems = 5;
        public const int OrderActors = 10;
        public const int OrderEffects = 50;

        public MapDef Map { get; private set; }

        Transform _root;
        bool[,] _solid;
        readonly Dictionary<Vector2Int, SpriteRenderer> _tiles = new Dictionary<Vector2Int, SpriteRenderer>();
        readonly Dictionary<Vector2Int, Action> _stepTriggers = new Dictionary<Vector2Int, Action>();
        readonly Dictionary<Vector2Int, Action> _interactions = new Dictionary<Vector2Int, Action>();
        readonly HashSet<Vector2Int> _blockers = new HashSet<Vector2Int>();

        static readonly Vector2Int[] Dirs = { Vector2Int.up, Vector2Int.down, Vector2Int.left, Vector2Int.right };

        public static Vector3 CellToWorld(Vector2Int c) => new Vector3(c.x, -c.y, 0f);

        public static Vector2Int WorldToCell(Vector3 w) => new Vector2Int(Mathf.RoundToInt(w.x), Mathf.RoundToInt(-w.y));

        public void Load(MapDef map)
        {
            if (_root != null) Destroy(_root.gameObject);
            _tiles.Clear();
            _stepTriggers.Clear();
            _interactions.Clear();
            _blockers.Clear();

            Map = map;
            _root = new GameObject("Mapa: " + map.Name).transform;
            _root.SetParent(transform, false);
            _solid = new bool[map.Width, map.Height];

            for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
            {
                var cell = new Vector2Int(x, y);
                char c = map.At(cell);
                if (TileLegend.IsMarker(c)) c = TileLegend.GroundUnder(map, cell);

                if (!TileLegend.TryGet(c, x, y, out var info))
                {
                    _solid[x, y] = true; // espaço vazio ou caractere desconhecido
                    if (c != ' ') Debug.LogWarning($"Mapa {map.Name}: caractere '{c}' sem tile em ({x},{y}).");
                    continue;
                }

                _solid[x, y] = info.Solid;
                _tiles[cell] = NewSprite("tile", info.Art, cell, OrderGround);
            }
        }

        SpriteRenderer NewSprite(string name, string[] art, Vector2Int cell, int order)
        {
            var go = new GameObject(name);
            go.transform.SetParent(_root, false);
            go.transform.position = CellToWorld(cell);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = art != null ? SpriteFactory.Get(art) : null;
            sr.sortingOrder = order;
            return sr;
        }

        /// <summary>Cria um objeto desenhado que pertence ao mapa atual (some quando o mapa troca).</summary>
        public SpriteRenderer SpawnSprite(string name, string[] art, Vector2Int cell, int order = OrderItems)
            => NewSprite(name, art, cell, order);

        public void SetTileArt(Vector2Int cell, string[] art)
        {
            if (_tiles.TryGetValue(cell, out var sr)) sr.sprite = SpriteFactory.Get(art);
        }

        public List<Vector2Int> FindAll(char c)
        {
            var list = new List<Vector2Int>();
            for (int y = 0; y < Map.Height; y++)
            for (int x = 0; x < Map.Width; x++)
                if (Map.Rows[y][x] == c) list.Add(new Vector2Int(x, y));
            return list;
        }

        public bool IsWalkable(Vector2Int c) => Map != null && Map.InBounds(c) && !_solid[c.x, c.y] && !_blockers.Contains(c);

        public void AddBlocker(Vector2Int c) => _blockers.Add(c);
        public void RemoveBlocker(Vector2Int c) => _blockers.Remove(c);

        // ---------------------------------------------------------- gatilhos e interações

        public void OnStep(Vector2Int cell, Action action) => _stepTriggers[cell] = action;
        public void ClearStep(Vector2Int cell) => _stepTriggers.Remove(cell);

        public bool TryStep(Vector2Int cell)
        {
            if (!_stepTriggers.TryGetValue(cell, out var action)) return false;
            action();
            return true;
        }

        public void OnInteract(Vector2Int cell, Action action) => _interactions[cell] = action;
        public bool HasInteraction(Vector2Int cell) => _interactions.ContainsKey(cell);

        public bool TryInteract(Vector2Int cell)
        {
            if (!_interactions.TryGetValue(cell, out var action)) return false;
            action();
            return true;
        }

        // ---------------------------------------------------------- caminho (toque pra andar)

        /// <summary>
        /// Busca em largura: menor caminho de <paramref name="from"/> até a primeira célula
        /// que satisfaz <paramref name="isGoal"/>. Retorna a lista sem a célula inicial, ou null.
        /// </summary>
        public List<Vector2Int> FindPath(Vector2Int from, Predicate<Vector2Int> isGoal)
        {
            if (isGoal(from)) return new List<Vector2Int>();

            var cameFrom = new Dictionary<Vector2Int, Vector2Int> { [from] = from };
            var queue = new Queue<Vector2Int>();
            queue.Enqueue(from);

            while (queue.Count > 0)
            {
                var cur = queue.Dequeue();
                foreach (var d in Dirs)
                {
                    var next = cur + d;
                    if (cameFrom.ContainsKey(next) || !IsWalkable(next)) continue;
                    cameFrom[next] = cur;
                    if (isGoal(next))
                    {
                        var path = new List<Vector2Int>();
                        for (var c = next; c != from; c = cameFrom[c]) path.Add(c);
                        path.Reverse();
                        return path;
                    }
                    queue.Enqueue(next);
                }
            }
            return null;
        }

        public static bool AreNeighbors(Vector2Int a, Vector2Int b)
            => Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y) == 1;
    }
}
