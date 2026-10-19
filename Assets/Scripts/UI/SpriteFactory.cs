using UnityEngine;

namespace Joaquim.UI
{
    /// <summary>Texturas simples geradas por código para a interface (retângulos e vinheta).</summary>
    public static class SpriteFactory
    {
        static Texture2D _white;
        static Texture2D _vignette;

        /// <summary>Textura 1x1 branca para desenhar retângulos de interface.</summary>
        public static Texture2D White
        {
            get
            {
                if (_white != null) return _white;
                _white = new Texture2D(1, 1, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
                _white.SetPixel(0, 0, Color.white);
                _white.Apply();
                return _white;
            }
        }

        /// <summary>Escurecimento nas bordas da tela.</summary>
        public static Texture2D Vignette
        {
            get
            {
                if (_vignette != null) return _vignette;
                const int size = 64;
                _vignette = new Texture2D(size, size, TextureFormat.RGBA32, false)
                {
                    filterMode = FilterMode.Bilinear,
                    wrapMode = TextureWrapMode.Clamp
                };
                var pixels = new Color32[size * size];
                float c = (size - 1) / 2f;
                for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                {
                    float dx = (x - c) / c, dy = (y - c) / c;
                    float d = Mathf.Clamp01(Mathf.Sqrt(dx * dx + dy * dy) / 1.25f);
                    byte a = (byte)(Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.45f, 1f, d)) * 235);
                    pixels[y * size + x] = new Color32(6, 18, 16, a);
                }
                _vignette.SetPixels32(pixels);
                _vignette.Apply();
                return _vignette;
            }
        }
    }
}
