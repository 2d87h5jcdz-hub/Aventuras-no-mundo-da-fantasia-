using Joaquim.Art;
using Joaquim.World;
using UnityEngine;

namespace Joaquim.Core
{
    /// <summary>
    /// Câmera ortográfica "pixel perfect": escolhe um zoom inteiro (cada pixel da arte vira
    /// N×N pixels da tela), segue o Joaquim e não deixa mostrar fora do mapa.
    /// </summary>
    [DefaultExecutionOrder(100)]
    public sealed class CameraRig : MonoBehaviour
    {
        /// <summary>Quantos tiles de altura queremos ver, aproximadamente.</summary>
        public float TargetTilesTall = 11f;

        public Transform Target;
        public GameWorld World;

        /// <summary>Intensidade do tremor (em tiles). A história liga e desliga.</summary>
        public float Shake;

        Camera _cam;
        int _lastHeight = -1;
        int _scale = 1;

        void Awake()
        {
            _cam = GetComponent<Camera>();
        }

        void LateUpdate()
        {
            UpdateZoom();
            if (Target == null || World == null || World.Map == null) return;

            var map = World.Map;
            float halfH = _cam.orthographicSize;
            float halfW = halfH * _cam.aspect;
            Vector3 t = Target.position;

            // Mundo: x vai de -0.5 até W-0.5; y vai de 0.5 até -(H-0.5)
            float x = map.Width <= halfW * 2f
                ? (map.Width - 1) / 2f
                : Mathf.Clamp(t.x, -0.5f + halfW, map.Width - 0.5f - halfW);
            float y = map.Height <= halfH * 2f
                ? -(map.Height - 1) / 2f
                : Mathf.Clamp(t.y, -(map.Height - 0.5f) + halfH, 0.5f - halfH);

            if (Shake > 0f)
            {
                x += Random.Range(-Shake, Shake);
                y += Random.Range(-Shake, Shake);
            }

            // Arredonda para o pixel da TELA, evitando "tremidinhas" e emendas entre tiles
            float unitsPerScreenPixel = 1f / (SpriteFactory.PixelsPerUnit * _scale);
            x = Mathf.Round(x / unitsPerScreenPixel) * unitsPerScreenPixel;
            y = Mathf.Round(y / unitsPerScreenPixel) * unitsPerScreenPixel;

            transform.position = new Vector3(x, y, -10f);
        }

        void UpdateZoom()
        {
            if (Screen.height == _lastHeight) return;
            _lastHeight = Screen.height;
            _scale = Mathf.Max(1, Mathf.RoundToInt(Screen.height / (SpriteFactory.PixelsPerUnit * TargetTilesTall)));
            _cam.orthographicSize = Screen.height / (float)(SpriteFactory.PixelsPerUnit * _scale) / 2f;
        }
    }
}
