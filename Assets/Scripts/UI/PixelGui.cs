using Joaquim.Art;
using UnityEngine;

namespace Joaquim.UI
{
    /// <summary>Utilitários de desenho de interface (IMGUI) com cara de jogo pixelado.</summary>
    public static class PixelGui
    {
        public static readonly Color Ink = new Color32(26, 28, 44, 255);
        public static readonly Color Panel = new Color32(41, 54, 111, 240);
        public static readonly Color Border = new Color32(244, 244, 244, 255);
        public static readonly Color Accent = new Color32(255, 205, 117, 255);

        /// <summary>Tamanho de um "pixel" de interface, proporcional à tela.</summary>
        public static float Unit => Mathf.Max(2f, Mathf.Round(Screen.height / 180f));

        /// <summary>Área segura (fora do notch) em coordenadas de IMGUI (origem no topo).</summary>
        public static Rect SafeArea
        {
            get
            {
                var s = Screen.safeArea;
                return new Rect(s.x, Screen.height - s.yMax, s.width, s.height);
            }
        }

        public static void Fill(Rect r, Color c)
        {
            var old = GUI.color;
            GUI.color = c;
            GUI.DrawTexture(r, SpriteFactory.White);
            GUI.color = old;
        }

        /// <summary>Caixa com borda dupla, cantos "cortados" no estilo 16 bits.</summary>
        public static void Box(Rect r, Color fill)
        {
            float u = Unit;
            // contorno escuro externo
            Fill(new Rect(r.x + u, r.y, r.width - 2 * u, r.height), Ink);
            Fill(new Rect(r.x, r.y + u, r.width, r.height - 2 * u), Ink);
            // borda clara
            var b = Inset(r, u);
            Fill(new Rect(b.x + u, b.y, b.width - 2 * u, b.height), Border);
            Fill(new Rect(b.x, b.y + u, b.width, b.height - 2 * u), Border);
            // miolo
            Fill(Inset(b, u), fill);
        }

        public static Rect Inset(Rect r, float by) => new Rect(r.x + by, r.y + by, r.width - 2 * by, r.height - 2 * by);

        public static GUIStyle Label(int size, TextAnchor anchor, Color color, FontStyle style = FontStyle.Normal)
        {
            var s = new GUIStyle(GUI.skin.label)
            {
                fontSize = size,
                alignment = anchor,
                wordWrap = true,
                richText = false,
                fontStyle = style,
                clipping = TextClipping.Overflow
            };
            s.normal.textColor = color;
            return s;
        }

        /// <summary>Texto com sombra de 1 "pixel" (fica legível sobre qualquer fundo).</summary>
        public static void ShadowLabel(Rect r, string text, GUIStyle style)
        {
            var c = style.normal.textColor;
            style.normal.textColor = new Color(0f, 0f, 0f, c.a * 0.8f);
            float u = Mathf.Max(1f, Unit * 0.5f);
            GUI.Label(new Rect(r.x + u, r.y + u, r.width, r.height), text, style);
            style.normal.textColor = c;
            GUI.Label(r, text, style);
        }
    }
}
