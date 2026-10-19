using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Joaquim.Core
{
    /// <summary>
    /// Ponto único de leitura de entrada (toque, mouse e teclado).
    /// Funciona tanto com o Input System novo quanto com o Input Manager antigo,
    /// para o projeto não quebrar se a configuração do Player mudar.
    /// </summary>
    public static class InputBridge
    {
        static int _consumedFrame = -1;

        /// <summary>
        /// Marca a entrada deste frame como já usada (ex.: o toque que fechou um diálogo
        /// não deve também mandar o personagem andar).
        /// </summary>
        public static void Consume() => _consumedFrame = Time.frameCount;

        static bool Consumed => _consumedFrame == Time.frameCount;

        /// <summary>Toque/clique iniciado neste frame, com a posição em pixels de tela.</summary>
        public static bool PointerPressed(out Vector2 screenPosition)
        {
            screenPosition = Vector2.zero;
            if (Consumed) return false;
#if ENABLE_INPUT_SYSTEM
            var touch = Touchscreen.current;
            if (touch != null)
            {
                // qualquer dedo (o outro pode estar segurando o joystick)
                foreach (var t in touch.touches)
                {
                    if (!t.press.wasPressedThisFrame) continue;
                    screenPosition = t.position.ReadValue();
                    return true;
                }
            }
            var mouse = Mouse.current;
            if (mouse != null && mouse.leftButton.wasPressedThisFrame)
            {
                screenPosition = mouse.position.ReadValue();
                return true;
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            for (int i = 0; i < Input.touchCount; i++)
            {
                var t = Input.GetTouch(i);
                if (t.phase != TouchPhase.Began) continue;
                screenPosition = t.position;
                return true;
            }
            if (Input.touchCount == 0 && Input.GetMouseButtonDown(0))
            {
                screenPosition = Input.mousePosition;
                return true;
            }
#endif
            return false;
        }

        /// <summary>Direção segurada: joystick da tela ou teclado (setas/WASD). Zero se nada.</summary>
        public static Vector2Int HeldDirection()
        {
            var stick = VirtualStick.Direction;
            if (stick != Vector2Int.zero) return stick;
#if ENABLE_INPUT_SYSTEM
            var kb = Keyboard.current;
            if (kb == null) return Vector2Int.zero;
            if (kb.upArrowKey.isPressed || kb.wKey.isPressed) return Vector2Int.up;
            if (kb.downArrowKey.isPressed || kb.sKey.isPressed) return Vector2Int.down;
            if (kb.leftArrowKey.isPressed || kb.aKey.isPressed) return Vector2Int.left;
            if (kb.rightArrowKey.isPressed || kb.dKey.isPressed) return Vector2Int.right;
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKey(KeyCode.UpArrow) || Input.GetKey(KeyCode.W)) return Vector2Int.up;
            if (Input.GetKey(KeyCode.DownArrow) || Input.GetKey(KeyCode.S)) return Vector2Int.down;
            if (Input.GetKey(KeyCode.LeftArrow) || Input.GetKey(KeyCode.A)) return Vector2Int.left;
            if (Input.GetKey(KeyCode.RightArrow) || Input.GetKey(KeyCode.D)) return Vector2Int.right;
#endif
            return Vector2Int.zero;
        }

        /// <summary>Tecla de ação (Espaço, Enter, Z ou E) pressionada neste frame.</summary>
        public static bool ActionKeyPressed()
        {
            if (Consumed) return false;
#if ENABLE_INPUT_SYSTEM
            var kb = Keyboard.current;
            return kb != null && (kb.spaceKey.wasPressedThisFrame || kb.enterKey.wasPressedThisFrame
                                  || kb.zKey.wasPressedThisFrame || kb.eKey.wasPressedThisFrame);
#elif ENABLE_LEGACY_INPUT_MANAGER
            return Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return)
                   || Input.GetKeyDown(KeyCode.Z) || Input.GetKeyDown(KeyCode.E);
#else
            return false;
#endif
        }

        /// <summary>Qualquer "confirmar": toque, clique ou tecla de ação.</summary>
        public static bool AnyConfirm()
        {
            return PointerPressed(out _) || ActionKeyPressed();
        }
    }
}
