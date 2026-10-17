using System.Collections;
using Joaquim.Audio;
using Joaquim.Core;
using UnityEngine;

namespace Joaquim.UI
{
    /// <summary>
    /// Caixa de diálogo com texto aparecendo letra por letra.
    /// Toque (ou Espaço) uma vez mostra o texto todo; de novo, fecha.
    /// </summary>
    [DefaultExecutionOrder(-50)] // lê o toque antes do Player
    public sealed class DialogueBox : MonoBehaviour
    {
        public static bool IsOpen { get; private set; }

        public float CharsPerSecond = 40f;

        string _speaker;
        string _text = "";
        Sprite _portrait;
        bool _narration;
        int _shown;
        float _acc;
        bool _done;
        int _openedFrame;

        GUIStyle _textStyle, _narrationStyle, _nameStyle;
        int _styleHeight = -1;

        /// <summary>Mostra uma fala e espera o jogador fechar.</summary>
        public IEnumerator Say(string speaker, string text, Sprite portrait)
        {
            _speaker = speaker;
            _text = text ?? "";
            _portrait = portrait;
            _narration = string.IsNullOrEmpty(speaker);
            _shown = 0;
            _acc = 0f;
            _done = _text.Length == 0;
            _openedFrame = Time.frameCount;
            IsOpen = true;
            while (IsOpen) yield return null;
        }

        void Update()
        {
            if (!IsOpen) return;

            if (!_done)
            {
                _acc += Time.deltaTime * CharsPerSecond;
                while (_acc >= 1f && _shown < _text.Length)
                {
                    _acc -= 1f;
                    _shown++;
                    if (_shown % 3 == 0 && !char.IsWhiteSpace(_text[_shown - 1])) Sfx.Blip();
                    // pausa curtinha depois de pontuação, como nos RPGs
                    char ch = _text[_shown - 1];
                    if (ch == '.' || ch == '!' || ch == '?' || ch == ',') _acc -= ch == ',' ? 3f : 6f;
                }
                if (_shown >= _text.Length) _done = true;
            }

            if (Time.frameCount == _openedFrame) return;
            if (!InputBridge.AnyConfirm()) return;

            InputBridge.Consume();
            if (!_done)
            {
                _shown = _text.Length;
                _done = true;
            }
            else
            {
                IsOpen = false;
            }
        }

        void OnDisable() => IsOpen = false;

        void EnsureStyles(float boxHeight)
        {
            if (_styleHeight == Screen.height && _textStyle != null) return;
            _styleHeight = Screen.height;
            int size = Mathf.Max(14, Mathf.RoundToInt(boxHeight * 0.155f));
            _textStyle = PixelGui.Label(size, TextAnchor.UpperLeft, Color.white);
            _narrationStyle = PixelGui.Label(size, TextAnchor.UpperLeft, PixelGui.Accent, FontStyle.Italic);
            _nameStyle = PixelGui.Label(Mathf.RoundToInt(size * 0.9f), TextAnchor.MiddleCenter, PixelGui.Accent, FontStyle.Bold);
            _nameStyle.wordWrap = false;
        }

        void OnGUI()
        {
            if (!IsOpen) return;
            GUI.depth = -10;

            var safe = PixelGui.SafeArea;
            float u = PixelGui.Unit;
            float h = Mathf.Round(Screen.height * 0.27f);
            float margin = Mathf.Round(Screen.height * 0.03f);
            EnsureStyles(h);

            var box = new Rect(safe.x + margin, safe.yMax - h - margin, safe.width - 2 * margin, h);
            PixelGui.Box(box, PixelGui.Panel);

            var content = PixelGui.Inset(box, u * 2 + Mathf.Round(h * 0.08f));

            if (_portrait != null)
            {
                float ps = content.height;
                var frame = new Rect(content.x, content.y, ps, ps);
                PixelGui.Box(frame, new Color32(148, 176, 194, 255));
                GUI.DrawTexture(PixelGui.Inset(frame, u * 3), _portrait.texture, ScaleMode.ScaleToFit);
                content.xMin += ps + Mathf.Round(h * 0.1f);
            }

            if (!_narration)
            {
                var size = _nameStyle.CalcSize(new GUIContent(_speaker));
                float tw = size.x + u * 10, th = size.y + u * 4;
                var tab = new Rect(box.x + u * 6, box.y - th + u * 2, tw, th);
                PixelGui.Box(tab, PixelGui.Ink);
                GUI.Label(tab, _speaker, _nameStyle);
            }

            var style = _narration ? _narrationStyle : _textStyle;
            PixelGui.ShadowLabel(content, _text.Substring(0, Mathf.Clamp(_shown, 0, _text.Length)), style);

            if (_done && Mathf.Repeat(Time.unscaledTime, 0.8f) < 0.5f)
            {
                float s = u * 3;
                PixelGui.Fill(new Rect(box.xMax - u * 6 - s, box.yMax - u * 5 - s, s, s), PixelGui.Accent);
            }
        }
    }
}
