using System.Collections.Generic;
using UnityEngine;

namespace Joaquim.Art
{
    /// <summary>
    /// Transforma os desenhos em texto (PixelArtData) em Sprites da Unity.
    /// 16 pixels = 1 unidade do mundo = 1 tile.
    /// </summary>
    public static class SpriteFactory
    {
        public const int PixelsPerUnit = 16;

        static readonly Dictionary<char, Color32> Colors = new Dictionary<char, Color32>();
        static readonly Dictionary<string[], Sprite> Cache = new Dictionary<string[], Sprite>();
        static Sprite _glow;
        static Texture2D _white;
        static Texture2D _vignette;

        static Color32 ColorOf(char c)
        {
            if (c == '.' || c == ' ') return new Color32(0, 0, 0, 0);
            if (Colors.TryGetValue(c, out var cached)) return cached;

            Color32 result = new Color32(255, 0, 255, 255); // magenta = cor desconhecida
            if (PixelArtData.Palette.TryGetValue(c, out var hex) && ColorUtility.TryParseHtmlString(hex, out var parsed))
                result = parsed;
            else
                Debug.LogWarning($"Cor '{c}' não existe na paleta.");
            Colors[c] = result;
            return result;
        }

        static Texture2D NewTexture(int w, int h, bool pixelated = true)
        {
            return new Texture2D(w, h, TextureFormat.RGBA32, false)
            {
                filterMode = pixelated ? FilterMode.Point : FilterMode.Bilinear,
                wrapMode = TextureWrapMode.Clamp
            };
        }

        /// <summary>Sprite 16x16 a partir de 16 linhas de texto (linha 0 = topo).</summary>
        public static Sprite Get(string[] rows)
        {
            if (Cache.TryGetValue(rows, out var sprite)) return sprite;

            int h = rows.Length;
            int w = rows[0].Length;
            var tex = NewTexture(w, h);
            var pixels = new Color32[w * h];
            for (int y = 0; y < h; y++)
            {
                string row = rows[h - 1 - y]; // textura cresce de baixo pra cima
                for (int x = 0; x < w; x++)
                    pixels[y * w + x] = x < row.Length ? ColorOf(row[x]) : new Color32(0, 0, 0, 0);
            }
            tex.SetPixels32(pixels);
            tex.Apply(false, false);

            sprite = Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f),
                PixelsPerUnit, 0, SpriteMeshType.FullRect);
            sprite.name = "pixel";
            Cache[rows] = sprite;
            return sprite;
        }

        /// <summary>Círculo de luz pixelado e com pontilhado nas bordas (efeito do relógio).</summary>
        public static Sprite Glow()
        {
            if (_glow != null) return _glow;
            const int size = 48;
            var tex = NewTexture(size, size);
            var pixels = new Color32[size * size];
            // Matriz de Bayer 4x4 para o pontilhado clássico de jogos 16 bits
            int[,] bayer = { { 0, 8, 2, 10 }, { 12, 4, 14, 6 }, { 3, 11, 1, 9 }, { 15, 7, 13, 5 } };
            var core = new Color32(255, 255, 255, 255);
            var mid = new Color32(255, 243, 176, 255);
            var outer = new Color32(115, 239, 247, 255);
            float c = (size - 1) / 2f;
            for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                float d = Mathf.Sqrt((x - c) * (x - c) + (y - c) * (y - c)) / (size / 2f);
                float threshold = (bayer[y % 4, x % 4] + 0.5f) / 16f;
                Color32 px = new Color32(0, 0, 0, 0);
                if (d < 0.35f) px = core;
                else if (d < 0.6f) px = (1f - (d - 0.35f) / 0.25f) > threshold ? core : mid;
                else if (d < 0.85f) px = (1f - (d - 0.6f) / 0.25f) > threshold ? mid : outer;
                else if (d < 1f && (1f - (d - 0.85f) / 0.15f) > threshold) px = outer;
                pixels[y * size + x] = px;
            }
            tex.SetPixels32(pixels);
            tex.Apply(false, false);
            _glow = Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f),
                PixelsPerUnit, 0, SpriteMeshType.FullRect);
            return _glow;
        }

        /// <summary>Textura 1x1 branca para desenhar retângulos de interface.</summary>
        public static Texture2D White
        {
            get
            {
                if (_white != null) return _white;
                _white = NewTexture(1, 1);
                _white.SetPixel(0, 0, Color.white);
                _white.Apply();
                return _white;
            }
        }

        /// <summary>Escurecimento nas bordas da tela (sensação de mata fechada).</summary>
        public static Texture2D Vignette
        {
            get
            {
                if (_vignette != null) return _vignette;
                const int size = 64;
                _vignette = NewTexture(size, size, pixelated: false);
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
