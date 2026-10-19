using UnityEngine;

namespace Joaquim.Render
{
    public enum QuadStyle { Cutout, Additive, Shadow }

    /// <summary>
    /// Um retângulo texturizado no mundo 3D: chão, parede, telhado ou "billboard" em pé
    /// (personagens, árvores, móveis). É a peça básica do visual HD-2D.
    /// </summary>
    public sealed class Quad : MonoBehaviour
    {
        static Material _cutout, _additive, _shadow;
        static readonly int MainTexId = Shader.PropertyToID("_MainTex");
        static readonly int ColorId = Shader.PropertyToID("_Color");
        static readonly int FlipId = Shader.PropertyToID("_Flip");
        static readonly int NoHazeId = Shader.PropertyToID("_NoHaze");

        MeshRenderer _renderer;
        MeshFilter _filter;
        MaterialPropertyBlock _block;
        Texture2D _tex;
        Color _color = Color.white;
        bool _flip, _noHaze;
        bool _billboard;
        float _scale = 1f;

        public Texture2D Texture => _tex;
        public bool Visible { get => _renderer.enabled; set => _renderer.enabled = value; }

        static Material MaterialFor(QuadStyle style)
        {
            switch (style)
            {
                case QuadStyle.Additive:
                    return _additive != null ? _additive : (_additive = NewMat("Joaquim/HD2D/Additive"));
                case QuadStyle.Shadow:
                    return _shadow != null ? _shadow : (_shadow = NewMat("Joaquim/HD2D/Shadow"));
                default:
                    return _cutout != null ? _cutout : (_cutout = NewMat("Joaquim/HD2D/Cutout"));
            }
        }

        static Material NewMat(string shaderName)
        {
            var shader = Shader.Find(shaderName);
            if (shader == null)
            {
                Debug.LogError("[Joaquim] Shader não encontrado: " + shaderName);
                shader = Shader.Find("Unlit/Transparent Cutout");
            }
            return new Material(shader) { name = shaderName };
        }

        static Quad NewObject(string name, Transform parent, QuadStyle style)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var q = go.AddComponent<Quad>();
            q._filter = go.AddComponent<MeshFilter>();
            q._renderer = go.AddComponent<MeshRenderer>();
            q._renderer.sharedMaterial = MaterialFor(style);
            q._renderer.receiveShadows = false;
            q._renderer.lightProbeUsage = UnityEngine.Rendering.LightProbeUsage.Off;
            q._renderer.reflectionProbeUsage = UnityEngine.Rendering.ReflectionProbeUsage.Off;
            // Sombra "ligada" para o shader entrar no mapa de profundidade (não há luzes na cena)
            q._renderer.shadowCastingMode = style == QuadStyle.Cutout
                ? UnityEngine.Rendering.ShadowCastingMode.On
                : UnityEngine.Rendering.ShadowCastingMode.Off;
            q._block = new MaterialPropertyBlock();
            return q;
        }

        /// <summary>
        /// Retângulo livre. <paramref name="origin"/> é o canto que corresponde ao topo-esquerdo
        /// da imagem; <paramref name="u"/> anda para a direita da imagem e <paramref name="v"/> para baixo.
        /// </summary>
        public static Quad Surface(string name, Transform parent, Texture2D tex, Vector3 origin, Vector3 u, Vector3 v,
            QuadStyle style = QuadStyle.Cutout)
        {
            var q = NewObject(name, parent, style);
            q._filter.sharedMesh = BuildMesh(origin, u, v);
            q._tex = tex;
            q.Apply();
            return q;
        }

        /// <summary>Imagem em pé, com o pé (base, centro) em <paramref name="foot"/>.</summary>
        public static Quad Billboard(string name, Transform parent, Texture2D tex, Vector3 foot, float scale = 1f,
            QuadStyle style = QuadStyle.Cutout)
        {
            var q = NewObject(name, parent, style);
            q.transform.position = foot;
            q._billboard = true;
            q._scale = scale;
            q._tex = tex;
            q.RebuildBillboard();
            q.Apply();
            return q;
        }

        /// <summary>Mancha deitada no chão (sombra ou poça de luz) centrada em <paramref name="center"/>.</summary>
        public static Quad Decal(string name, Transform parent, Texture2D tex, Vector3 center, Vector2 size,
            QuadStyle style, float height = 0.02f)
        {
            var o = new Vector3(-size.x / 2f, height, size.y / 2f);
            var q = NewObject(name, parent, style);
            q.transform.position = new Vector3(center.x, 0f, center.z);
            q._filter.sharedMesh = BuildMesh(o, new Vector3(size.x, 0, 0), new Vector3(0, 0, -size.y));
            q._tex = tex;
            q.Apply();
            return q;
        }

        void RebuildBillboard()
        {
            var s = Art.SizeOf(_tex) * _scale;
            if (_filter.sharedMesh != null) Destroy(_filter.sharedMesh);
            _filter.sharedMesh = BuildMesh(new Vector3(-s.x / 2f, s.y, 0f), new Vector3(s.x, 0, 0), new Vector3(0, -s.y, 0));
        }

        static Mesh BuildMesh(Vector3 o, Vector3 u, Vector3 v)
        {
            var m = new Mesh { name = "quad" };
            m.vertices = new[] { o, o + u, o + v, o + u + v };
            m.uv = new[] { new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, 0), new Vector2(1, 0) };
            m.triangles = new[] { 0, 1, 2, 2, 1, 3 };
            var n = Vector3.Cross(u, v).normalized;
            m.normals = new[] { n, n, n, n };
            m.RecalculateBounds();
            return m;
        }

        public void SetTexture(Texture2D tex)
        {
            if (tex == null || tex == _tex) return;
            bool resize = _billboard && (tex.width != _tex.width || tex.height != _tex.height);
            _tex = tex;
            if (resize) RebuildBillboard();
            Apply();
        }

        public void SetColor(Color c) { _color = c; Apply(); }
        public void SetFlip(bool flip) { if (flip == _flip) return; _flip = flip; Apply(); }
        public void SetNoHaze(bool noHaze) { _noHaze = noHaze; Apply(); }

        public void SetScale(float scale)
        {
            if (!_billboard) { transform.localScale = Vector3.one * scale; return; }
            _scale = scale;
            RebuildBillboard();
        }

        void Apply()
        {
            _renderer.GetPropertyBlock(_block);
            _block.SetTexture(MainTexId, _tex);
            _block.SetColor(ColorId, _color);
            _block.SetFloat(FlipId, _flip ? 1f : 0f);
            _block.SetFloat(NoHazeId, _noHaze ? 1f : 0f);
            _renderer.SetPropertyBlock(_block);
        }

        void OnDestroy()
        {
            if (_filter != null && _filter.sharedMesh != null) Destroy(_filter.sharedMesh);
        }
    }
}
