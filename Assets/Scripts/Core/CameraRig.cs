using Joaquim.Render;
using Joaquim.World;
using UnityEngine;

namespace Joaquim.Core
{
    /// <summary>
    /// Câmera 3D em perspectiva (estilo HD-2D): olha o Joaquim um pouco de cima,
    /// segue de forma suave, não mostra demais além das bordas e mantém o foco nele.
    /// </summary>
    [DefaultExecutionOrder(100)]
    public sealed class CameraRig : MonoBehaviour
    {
        public Transform Target;
        public GameWorld World;
        public HD2DPost Post;

        /// <summary>Intensidade do tremor (em unidades). A história liga e desliga.</summary>
        public float Shake;

        Camera _cam;
        Vector3 _smoothTarget;
        bool _snap = true;

        void Awake()
        {
            _cam = GetComponent<Camera>();
        }

        /// <summary>Pula direto para o alvo (ao trocar de mapa).</summary>
        public void Snap() => _snap = true;

        void LateUpdate()
        {
            if (Target == null || World == null || World.Map == null) return;
            var p = World.Preset;
            var map = World.Map;

            _cam.fieldOfView = p.CamFov;
            _cam.backgroundColor = p.Background;

            var aim = Target.position + Vector3.up * p.CamTargetHeight;

            // limita o x para não mostrar muito além das bordas do mapa
            float hfov = Mathf.Atan(Mathf.Tan(p.CamFov * Mathf.Deg2Rad / 2f) * _cam.aspect);
            float half = Mathf.Tan(hfov) * p.CamDistance;
            float minX = -0.5f - p.CamSidePadding, maxX = map.Width - 0.5f + p.CamSidePadding;
            aim.x = maxX - minX <= half * 2f ? (minX + maxX) / 2f : Mathf.Clamp(aim.x, minX + half, maxX - half);

            if (_snap)
            {
                _smoothTarget = aim;
                _snap = false;
            }
            else
            {
                _smoothTarget = Vector3.Lerp(_smoothTarget, aim, 1f - Mathf.Exp(-Time.deltaTime * 8f));
            }

            var rot = Quaternion.Euler(p.CamPitch, 0f, 0f);
            var pos = _smoothTarget - rot * Vector3.forward * p.CamDistance;
            if (Shake > 0f)
                pos += new Vector3(Random.Range(-Shake, Shake), Random.Range(-Shake, Shake), 0f);

            transform.SetPositionAndRotation(pos, rot);

            if (Post != null)
            {
                Post.Preset = p;
                Post.FocusDistance = Vector3.Distance(pos, Target.position + Vector3.up * 1f);
            }
        }
    }
}
