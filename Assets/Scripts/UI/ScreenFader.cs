using System.Collections;
using UnityEngine;

namespace Joaquim.UI
{
    /// <summary>
    /// Camada por cima do jogo: escurecer/clarear a tela, letreiros (título, capítulo)
    /// e a vinheta escura da floresta.
    /// </summary>
    public sealed class ScreenFader : MonoBehaviour
    {
        public Color OverlayColor = Color.black;
        [Range(0, 1)] public float Alpha;
        public bool Vignette;

        string _title, _subtitle;
        bool _blinkSubtitle;
        float _captionAlpha;
        GUIStyle _titleStyle, _subStyle;
        int _styleHeight = -1;

        public void Set(Color color, float alpha)
        {
            OverlayColor = color;
            Alpha = alpha;
        }

        /// <summary>Vai da cor/opacidade atual até a nova, em <paramref name="seconds"/>.</summary>
        public IEnumerator FadeTo(Color color, float alpha, float seconds)
        {
            Color fromColor = OverlayColor;
            float fromAlpha = Alpha;
            // Se a tela está transparente, troca a cor direto (evita "passar pelo cinza")
            if (fromAlpha <= 0.001f) fromColor = color;
            for (float t = 0; t < seconds; t += Time.deltaTime)
            {
                float k = Mathf.SmoothStep(0f, 1f, t / seconds);
                OverlayColor = Color.Lerp(fromColor, color, k);
                Alpha = Mathf.Lerp(fromAlpha, alpha, k);
                yield return null;
            }
            OverlayColor = color;
            Alpha = alpha;
        }

        public void ShowCaption(string title, string subtitle = null, bool blinkSubtitle = false)
        {
            _title = title;
            _subtitle = subtitle;
            _blinkSubtitle = blinkSubtitle;
            _captionAlpha = 1f;
        }

        public IEnumerator FadeCaption(float to, float seconds)
        {
            float from = _captionAlpha;
            for (float t = 0; t < seconds; t += Time.deltaTime)
            {
                _captionAlpha = Mathf.Lerp(from, to, t / seconds);
                yield return null;
            }
            _captionAlpha = to;
            if (to <= 0f) HideCaption();
        }

        public void HideCaption()
        {
            _title = _subtitle = null;
            _captionAlpha = 0f;
        }

        void OnGUI()
        {
            GUI.depth = 10;
            var full = new Rect(0, 0, Screen.width, Screen.height);

            if (Vignette)
                GUI.DrawTexture(full, SpriteFactory.Vignette, ScaleMode.StretchToFill);

            if (Alpha > 0f)
            {
                var c = OverlayColor;
                c.a = Alpha;
                PixelGui.Fill(full, c);
            }

            if (_captionAlpha <= 0f || (_title == null && _subtitle == null)) return;

            if (_styleHeight != Screen.height || _titleStyle == null)
            {
                _styleHeight = Screen.height;
                _titleStyle = PixelGui.Label(Mathf.RoundToInt(Screen.height / 11f), TextAnchor.MiddleCenter, Color.white, FontStyle.Bold);
                _subStyle = PixelGui.Label(Mathf.RoundToInt(Screen.height / 24f), TextAnchor.MiddleCenter, PixelGui.Accent);
            }

            // texto escuro sobre fundo claro (tela branca), claro sobre fundo escuro
            bool lightBg = Alpha > 0.5f && OverlayColor.grayscale > 0.6f;
            var titleColor = lightBg ? PixelGui.Ink : Color.white;
            var subColor = lightBg ? (Color)new Color32(93, 39, 93, 255) : PixelGui.Accent;

            var safe = PixelGui.SafeArea;
            if (_title != null)
            {
                _titleStyle.normal.textColor = new Color(titleColor.r, titleColor.g, titleColor.b, _captionAlpha);
                var r = new Rect(safe.x, safe.y + safe.height * 0.25f, safe.width, safe.height * 0.3f);
                PixelGui.ShadowLabel(r, _title, _titleStyle);
            }
            if (_subtitle != null && (!_blinkSubtitle || Mathf.Repeat(Time.unscaledTime, 1.2f) < 0.8f))
            {
                _subStyle.normal.textColor = new Color(subColor.r, subColor.g, subColor.b, _captionAlpha);
                var r = new Rect(safe.x, safe.y + safe.height * 0.58f, safe.width, safe.height * 0.15f);
                PixelGui.ShadowLabel(r, _subtitle, _subStyle);
            }
        }
    }
}
