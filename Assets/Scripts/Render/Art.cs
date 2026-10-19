using System.Collections.Generic;
using UnityEngine;

namespace Joaquim.Render
{
    /// <summary>
    /// Carrega as imagens geradas por tools/arte/gerar.py (Assets/Resources/Art).
    /// 16 pixels da imagem = 1 unidade do mundo = 1 tile.
    /// </summary>
    public static class Art
    {
        public const float PixelsPerUnit = 16f;

        static readonly Dictionary<string, Texture2D> Cache = new Dictionary<string, Texture2D>();
        static Texture2D _missing;

        public static Texture2D Tex(string path)
        {
            if (Cache.TryGetValue(path, out var t)) return t;
            t = Resources.Load<Texture2D>("Art/" + path);
            if (t == null)
            {
                Debug.LogError("[Joaquim] Imagem não encontrada: Art/" + path + " (rodou tools/arte/gerar.py?)");
                t = Missing;
            }
            Cache[path] = t;
            return t;
        }

        static Texture2D Missing
        {
            get
            {
                if (_missing != null) return _missing;
                _missing = new Texture2D(2, 2) { filterMode = FilterMode.Point };
                _missing.SetPixels(new[] { Color.magenta, Color.black, Color.black, Color.magenta });
                _missing.Apply();
                return _missing;
            }
        }

        /// <summary>Tamanho em unidades do mundo.</summary>
        public static Vector2 SizeOf(Texture2D t) => new Vector2(t.width / PixelsPerUnit, t.height / PixelsPerUnit);
    }
}
