using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Joaquim.Core
{
    /// <summary>
    /// Joystick flutuante: aparece onde o dedo encosta na metade esquerda da tela
    /// e some ao soltar. Dá a direção em 4 sentidos (o Joaquim anda em grade).
    /// </summary>
    [DefaultExecutionOrder(-100)]
    public sealed class VirtualStick : MonoBehaviour
    {
        /// <summary>Direção atual (cima = y positivo, como na tela). Zero se solto.</summary>
        public static Vector2Int Direction { get; private set; }

        /// <summary>Fração da largura da tela, a partir da esquerda, que ativa o joystick.</summary>
        public static float ZoneWidth = 0.5f;

        bool _active;
        int _fingerId = -1;
        bool _mouse;
        Vector2 _origin, _current;
        float _alpha;

        static Texture2D _ring, _knob;

        static float Radius => Mathf.Max(40f, Screen.height * 0.1f);

        public static bool InZone(Vector2 screenPos) => screenPos.x < Screen.width * ZoneWidth;

        void Update()
        {
            if (!_active) TryBegin();
            else Track();

            Direction = _active ? ComputeDirection() : Vector2Int.zero;
            _alpha = Mathf.MoveTowards(_alpha, _active ? 1f : 0f, Time.unscaledDeltaTime * 8f);
        }

        void Begin(Vector2 pos, int finger, bool mouse)
        {
            _active = true;
            _fingerId = finger;
            _mouse = mouse;
            _origin = _current = pos;
        }

        void TryBegin()
        {
#if ENABLE_INPUT_SYSTEM
            var ts = Touchscreen.current;
            if (ts != null)
            {
                foreach (var t in ts.touches)
                {
                    if (!t.press.wasPressedThisFrame) continue;
                    var p = t.position.ReadValue();
                    if (InZone(p)) { Begin(p, t.touchId.ReadValue(), false); return; }
                }
            }
            var m = Mouse.current;
            if ((ts == null || !ts.press.isPressed) && m != null && m.leftButton.wasPressedThisFrame)
            {
                var p = m.position.ReadValue();
                if (InZone(p)) Begin(p, -1, true);
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            for (int i = 0; i < Input.touchCount; i++)
            {
                var t = Input.GetTouch(i);
                if (t.phase == TouchPhase.Began && InZone(t.position)) { Begin(t.position, t.fingerId, false); return; }
            }
            if (Input.touchCount == 0 && Input.GetMouseButtonDown(0) && InZone(Input.mousePosition))
                Begin(Input.mousePosition, -1, true);
#endif
        }

        void Track()
        {
            bool held = false;
            Vector2 pos = _current;
#if ENABLE_INPUT_SYSTEM
            if (_mouse)
            {
                var m = Mouse.current;
                if (m != null && m.leftButton.isPressed) { held = true; pos = m.position.ReadValue(); }
            }
            else if (Touchscreen.current != null)
            {
                foreach (var t in Touchscreen.current.touches)
                {
                    if (t.touchId.ReadValue() != _fingerId || !t.press.isPressed) continue;
                    held = true;
                    pos = t.position.ReadValue();
                    break;
                }
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (_mouse)
            {
                if (Input.GetMouseButton(0)) { held = true; pos = Input.mousePosition; }
            }
            else
            {
                for (int i = 0; i < Input.touchCount; i++)
                {
                    var t = Input.GetTouch(i);
                    if (t.fingerId != _fingerId) continue;
                    if (t.phase != TouchPhase.Ended && t.phase != TouchPhase.Canceled) { held = true; pos = t.position; }
                    break;
                }
            }
#endif
            if (!held)
            {
                _active = false;
                _fingerId = -1;
                return;
            }
            _current = pos;
            // se o dedo passar da borda, a base vem junto (não precisa voltar o dedo)
            var d = _current - _origin;
            float r = Radius;
            if (d.magnitude > r) _origin = _current - d.normalized * r;
        }

        Vector2Int ComputeDirection()
        {
            var d = _current - _origin;
            if (d.magnitude < Radius * 0.3f) return Vector2Int.zero;
            if (Mathf.Abs(d.x) > Mathf.Abs(d.y)) return d.x > 0 ? Vector2Int.right : Vector2Int.left;
            return d.y > 0 ? Vector2Int.up : Vector2Int.down;
        }

        void OnDisable()
        {
            _active = false;
            Direction = Vector2Int.zero;
        }

        // ------------------------------------------------------------ desenho

        void OnGUI()
        {
            if (_alpha <= 0.01f) return;
            GUI.depth = -5;
            EnsureTextures();
            float r = Radius;
            // IMGUI tem y para baixo
            var o = new Vector2(_origin.x, Screen.height - _origin.y);
            var c = new Vector2(_current.x, Screen.height - _current.y);
            var knobPos = o + Vector2.ClampMagnitude(c - o, r);

            var old = GUI.color;
            GUI.color = new Color(1f, 1f, 1f, 0.55f * _alpha);
            GUI.DrawTexture(new Rect(o.x - r, o.y - r, r * 2, r * 2), _ring);
            var dir = ComputeDirection();
            if (dir != Vector2Int.zero)
            {
                // destaca a direção escolhida
                var dv = new Vector2(dir.x, -dir.y) * r * 0.72f;
                float s = r * 0.32f;
                GUI.color = new Color(1f, 0.85f, 0.45f, 0.8f * _alpha);
                GUI.DrawTexture(new Rect(o.x + dv.x - s / 2, o.y + dv.y - s / 2, s, s), _knob);
            }
            float k = r * 0.8f;
            GUI.color = new Color(1f, 1f, 1f, 0.75f * _alpha);
            GUI.DrawTexture(new Rect(knobPos.x - k / 2, knobPos.y - k / 2, k, k), _knob);
            GUI.color = old;
        }

        static void EnsureTextures()
        {
            if (_ring == null) _ring = Circle(64, ring: true);
            if (_knob == null) _knob = Circle(32, ring: false);
        }

        /// <summary>Círculo pixelado (estilo do jogo), com contorno escuro.</summary>
        static Texture2D Circle(int size, bool ring)
        {
            var t = new Texture2D(size, size, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[size * size];
            float c = (size - 1) / 2f, R = size / 2f - 1;
            var ink = new Color32(26, 28, 44, 255);
            var fill = new Color32(244, 244, 244, 255);
            var dark = new Color32(148, 176, 194, 255);
            for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                float d = Mathf.Sqrt((x - c) * (x - c) + (y - c) * (y - c));
                Color32 col = new Color32(0, 0, 0, 0);
                if (ring)
                {
                    if (d <= R && d > R - 2) col = ink;
                    else if (d <= R - 2 && d > R - 5) col = fill;
                    else if (d <= R - 5 && d > R - 6) col = ink;
                    else if (d <= R - 6) col = new Color32(26, 28, 44, 90);
                }
                else
                {
                    if (d <= R && d > R - 2) col = ink;
                    else if (d <= R - 2) col = (y > c + 2 && d > R * 0.35f) ? fill : (d < R * 0.35f && y > c ? fill : dark);
                }
                px[y * size + x] = col;
            }
            t.SetPixels32(px);
            t.Apply();
            return t;
        }
    }
}
