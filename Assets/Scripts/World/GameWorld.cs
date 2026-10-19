using System;
using System.Collections.Generic;
using Joaquim.Render;
using UnityEngine;

namespace Joaquim.World
{
    /// <summary>
    /// Monta o mapa atual em 3D e responde perguntas sobre ele:
    /// dá pra andar aqui? tem gatilho? tem algo pra interagir?
    /// Coordenadas: célula (x, y) do mapa, com y crescendo pra baixo; no mundo vira (x, 0, -y).
    /// </summary>
    public sealed class GameWorld : MonoBehaviour
    {
        public MapDef Map { get; private set; }
        public ScenePreset Preset { get; set; } = new ScenePreset();
        public Transform Root { get; private set; }

        /// <summary>Peças que a história troca de imagem (porta, cama).</summary>
        public Quad Door { get; set; }
        public Quad BedTop { get; set; }

        bool[,] _solid;
        readonly Dictionary<Vector2Int, Action> _stepTriggers = new Dictionary<Vector2Int, Action>();
        readonly Dictionary<Vector2Int, Action> _interactions = new Dictionary<Vector2Int, Action>();
        readonly Dictionary<Vector2Int, float> _interactionHeight = new Dictionary<Vector2Int, float>();
        readonly HashSet<Vector2Int> _blockers = new HashSet<Vector2Int>();

        static readonly Vector2Int[] Dirs = { Vector2Int.up, Vector2Int.down, Vector2Int.left, Vector2Int.right };

        public static Vector3 CellToWorld(Vector2Int c) => new Vector3(c.x, 0f, -c.y);

        public static Vector2Int WorldToCell(Vector3 w) => new Vector2Int(Mathf.RoundToInt(w.x), Mathf.RoundToInt(-w.z));

        public void Load(MapDef map)
        {
            if (Root != null) Destroy(Root.gameObject);
            _stepTriggers.Clear();
            _interactions.Clear();
            _interactionHeight.Clear();
            _blockers.Clear();
            Door = null;
            BedTop = null;

            Map = map;
            Root = new GameObject("Mapa: " + map.Name).transform;
            Root.SetParent(transform, false);

            _solid = new bool[map.Width, map.Height];
            for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
                _solid[x, y] = TileLegend.IsSolid(map.Rows[y][x]);

            Preset = SceneBuilder.Build(this, map);
            Shader.SetGlobalColor("_HazeColor", Preset.HazeColor);
            Shader.SetGlobalFloat("_HazeDensity", Preset.HazeDensity);
            Shader.SetGlobalFloat("_HazeStrength", Preset.HazeStrength);
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

        // ---------------------------------------------------------- objetos criados pela história

        /// <summary>Imagem em pé numa célula (some quando o mapa troca).</summary>
        public Quad SpawnBillboard(string name, Texture2D tex, Vector2Int cell, QuadStyle style = QuadStyle.Cutout,
            float scale = 1f, float lift = 0f)
        {
            var q = Quad.Billboard(name, Root, tex, CellToWorld(cell) + Vector3.up * lift, scale, style);
            if (style == QuadStyle.Cutout) q.SetColor(Preset.PropTint);
            return q;
        }

        public Quad SpawnShadow(Vector3 foot, float radius, Transform parent = null)
        {
            var off = new Vector3(Preset.ShadowOffset.x, 0f, Preset.ShadowOffset.y) * radius;
            var q = Quad.Decal("sombra", parent != null ? parent : Root, Art.Tex("Efeitos/sombra"), foot + off,
                new Vector2(radius * 2.4f, radius * 1.1f), QuadStyle.Shadow);
            q.SetColor(Preset.ShadowColor);
            if (parent != null) q.transform.localPosition = off;
            return q;
        }

        public Quad SpawnLight(Vector3 center, float radius, Color color)
        {
            var q = Quad.Decal("luz", Root, Art.Tex("Efeitos/luz"), center, new Vector2(radius * 2f, radius * 2f),
                QuadStyle.Additive, 0.03f);
            q.SetColor(color);
            return q;
        }

        // ---------------------------------------------------------- gatilhos e interações

        public void OnStep(Vector2Int cell, Action action) => _stepTriggers[cell] = action;
        public void ClearStep(Vector2Int cell) => _stepTriggers.Remove(cell);

        public bool TryStep(Vector2Int cell)
        {
            if (!_stepTriggers.TryGetValue(cell, out var action)) return false;
            action();
            return true;
        }

        /// <summary>Algo que dá pra tocar/usar. <paramref name="height"/> é a altura da figura (para o toque na tela).</summary>
        public void OnInteract(Vector2Int cell, Action action, float height = 1f)
        {
            _interactions[cell] = action;
            _interactionHeight[cell] = height;
        }

        public bool HasInteraction(Vector2Int cell) => _interactions.ContainsKey(cell);

        public bool TryInteract(Vector2Int cell)
        {
            if (!_interactions.TryGetValue(cell, out var action)) return false;
            action();
            return true;
        }

        /// <summary>O toque acertou a figura de algo interativo? (testa a "placa" em pé de cada um)</summary>
        public bool PickInteraction(Ray ray, out Vector2Int cell)
        {
            cell = default;
            float best = float.MaxValue;
            bool found = false;
            foreach (var kv in _interactionHeight)
            {
                var c = kv.Key;
                float planeZ = -c.y;
                if (Mathf.Abs(ray.direction.z) < 1e-4f) continue;
                float t = (planeZ - ray.origin.z) / ray.direction.z;
                if (t <= 0f || t >= best) continue;
                var p = ray.GetPoint(t);
                if (Mathf.Abs(p.x - c.x) <= 0.6f && p.y >= -0.1f && p.y <= kv.Value)
                {
                    best = t;
                    cell = c;
                    found = true;
                }
            }
            return found;
        }

        /// <summary>Célula do chão que o toque acertou.</summary>
        public static bool PickGround(Ray ray, out Vector2Int cell)
        {
            cell = default;
            if (ray.direction.y > -1e-4f) return false;
            float t = -ray.origin.y / ray.direction.y;
            cell = WorldToCell(ray.GetPoint(t));
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
