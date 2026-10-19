using System.Collections.Generic;
using UnityEngine;

namespace Joaquim.Render
{
    /// <summary>Pontinhos de luz flutuando em volta da câmera (pólen, poeira, vaga-lumes).</summary>
    public sealed class Motes : MonoBehaviour
    {
        public Transform Follow;
        public Vector3 Area = new Vector3(14f, 4f, 10f);

        readonly List<Quad> _quads = new List<Quad>();
        readonly List<Vector3> _base = new List<Vector3>();
        readonly List<Vector4> _phase = new List<Vector4>();
        Color _color;

        public void Configure(int count, Color color, float size)
        {
            foreach (var q in _quads) if (q != null) Destroy(q.gameObject);
            _quads.Clear(); _base.Clear(); _phase.Clear();
            _color = color;
            var tex = Art.Tex("Efeitos/pontinho");
            for (int i = 0; i < count; i++)
            {
                var q = Quad.Billboard("partícula", transform, tex, Vector3.zero, size * Random.Range(0.6f, 1.4f) * 2f,
                    QuadStyle.Additive);
                _quads.Add(q);
                _base.Add(new Vector3(Random.Range(-.5f, .5f) * Area.x, Random.Range(0.2f, 1f) * Area.y,
                    Random.Range(-.5f, .5f) * Area.z));
                _phase.Add(new Vector4(Random.value * 10f, Random.Range(0.2f, 0.6f), Random.Range(0.3f, 1.2f),
                    Random.value * 10f));
            }
        }

        void LateUpdate()
        {
            if (Follow == null) return;
            var c = Follow.position;
            float t = Time.time;
            for (int i = 0; i < _quads.Count; i++)
            {
                var b = _base[i];
                var ph = _phase[i];
                var p = new Vector3(
                    b.x + Mathf.Sin(t * ph.y + ph.x) * 0.8f,
                    b.y + Mathf.Sin(t * ph.z * 0.7f + ph.w) * 0.4f,
                    b.z + Mathf.Cos(t * ph.y * 0.8f + ph.w) * 0.6f);
                // mantém a nuvem de partículas em volta de quem a câmera segue
                _quads[i].transform.position = new Vector3(c.x + Wrap(p.x, Area.x), p.y, c.z + Wrap(p.z, Area.z));
                float blink = 0.55f + 0.45f * Mathf.Sin(t * ph.z * 2.1f + ph.x);
                var col = _color;
                col.a *= blink;
                _quads[i].SetColor(col);
            }
        }

        static float Wrap(float v, float size) => Mathf.Repeat(v + size / 2f, size) - size / 2f;
    }
}
