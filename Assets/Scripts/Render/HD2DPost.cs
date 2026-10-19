using UnityEngine;

namespace Joaquim.Render
{
    /// <summary>
    /// Efeitos de tela do estilo HD-2D (pipeline padrão da Unity, via OnRenderImage):
    /// desfoque por profundidade, bloom, raios de sol, cor e vinheta.
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public sealed class HD2DPost : MonoBehaviour
    {
        public ScenePreset Preset = new ScenePreset();

        /// <summary>Distância da câmera até o que deve ficar nítido (o Joaquim).</summary>
        public float FocusDistance = 13f;

        Material _mat;
        bool _failed;

        static readonly int BlurDir = Shader.PropertyToID("_BlurDir");
        static readonly int BlurTex = Shader.PropertyToID("_BlurTex");
        static readonly int BloomTex = Shader.PropertyToID("_BloomTex");

        void Awake()
        {
            GetComponent<Camera>().depthTextureMode |= DepthTextureMode.Depth;
        }

        bool Ready()
        {
            if (_mat != null) return true;
            if (_failed) return false;
            var shader = Shader.Find("Hidden/Joaquim/HD2DPost");
            if (shader == null || !shader.isSupported)
            {
                Debug.LogWarning("[Joaquim] Pós-processamento indisponível neste aparelho; seguindo sem ele.");
                _failed = true;
                return false;
            }
            _mat = new Material(shader) { hideFlags = HideFlags.HideAndDontSave };
            return true;
        }

        void OnRenderImage(RenderTexture src, RenderTexture dst)
        {
            if (!Ready())
            {
                Graphics.Blit(src, dst);
                return;
            }

            var p = Preset;
            _mat.SetFloat("_Threshold", p.BloomThreshold);
            _mat.SetFloat("_FocusDist", Mathf.Max(0.5f, FocusDistance));
            _mat.SetFloat("_DofStrength", p.DofStrength);
            _mat.SetFloat("_DofMax", p.DofMax);
            _mat.SetFloat("_BloomIntensity", p.BloomIntensity);
            _mat.SetColor("_BloomTint", p.BloomTint);
            _mat.SetFloat("_Vignette", p.Vignette);
            _mat.SetFloat("_Saturation", p.Saturation);
            _mat.SetFloat("_Contrast", p.Contrast);
            _mat.SetColor("_ShadowTint", p.ShadowTint);
            _mat.SetColor("_Grade", p.Grade);
            _mat.SetFloat("_RaysIntensity", p.RaysIntensity);
            _mat.SetFloat("_RaysAngle", p.RaysAngle);
            _mat.SetColor("_RaysColor", p.RaysColor);

            // versão desfocada (metade da resolução) para o desfoque de profundidade
            int hw = Mathf.Max(1, src.width / 2), hh = Mathf.Max(1, src.height / 2);
            var blurA = RenderTexture.GetTemporary(hw, hh, 0, src.format);
            var blurB = RenderTexture.GetTemporary(hw, hh, 0, src.format);
            blurA.filterMode = blurB.filterMode = FilterMode.Bilinear;
            Graphics.Blit(src, blurA);
            Blur(blurA, blurB, 1f);
            Blur(blurA, blurB, 2f);

            // bloom (um quarto da resolução, desfoque largo)
            int qw = Mathf.Max(1, src.width / 4), qh = Mathf.Max(1, src.height / 4);
            var bloomA = RenderTexture.GetTemporary(qw, qh, 0, src.format);
            var bloomB = RenderTexture.GetTemporary(qw, qh, 0, src.format);
            bloomA.filterMode = bloomB.filterMode = FilterMode.Bilinear;
            Graphics.Blit(src, bloomA, _mat, 0);
            Blur(bloomA, bloomB, 1f);
            Blur(bloomA, bloomB, 2.5f);
            Blur(bloomA, bloomB, 4f);

            _mat.SetTexture(BlurTex, blurA);
            _mat.SetTexture(BloomTex, bloomA);
            Graphics.Blit(src, dst, _mat, 2);

            RenderTexture.ReleaseTemporary(blurA);
            RenderTexture.ReleaseTemporary(blurB);
            RenderTexture.ReleaseTemporary(bloomA);
            RenderTexture.ReleaseTemporary(bloomB);
        }

        /// <summary>Desfoque horizontal + vertical; o resultado volta para <paramref name="a"/>.</summary>
        void Blur(RenderTexture a, RenderTexture b, float spread)
        {
            _mat.SetVector(BlurDir, new Vector4(spread, 0, 0, 0));
            Graphics.Blit(a, b, _mat, 1);
            _mat.SetVector(BlurDir, new Vector4(0, spread, 0, 0));
            Graphics.Blit(b, a, _mat, 1);
        }

        void OnDestroy()
        {
            if (_mat != null) Destroy(_mat);
        }
    }
}
