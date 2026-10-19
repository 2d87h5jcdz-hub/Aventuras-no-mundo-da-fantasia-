using Joaquim.Render;
using UnityEngine;

namespace Joaquim.Actors
{
    /// <summary>Troca as imagens de um Quad em sequência (null = esconde naquele quadro).</summary>
    public sealed class FrameAnimator : MonoBehaviour
    {
        Texture2D[] _frames;
        float[] _durations;
        Quad _quad;
        int _index;
        float _timer;

        public void Play(Texture2D[] frames, float[] durations)
        {
            _frames = frames;
            _durations = durations;
            _quad = GetComponent<Quad>();
            _index = 0;
            _timer = 0f;
            Apply();
        }

        void Update()
        {
            if (_frames == null || _frames.Length == 0) return;
            _timer += Time.deltaTime;
            float d = _durations[Mathf.Min(_index, _durations.Length - 1)];
            if (_timer < d) return;
            _timer -= d;
            _index = (_index + 1) % _frames.Length;
            Apply();
        }

        void Apply()
        {
            var tex = _frames[_index];
            _quad.Visible = tex != null;
            if (tex != null) _quad.SetTexture(tex);
        }
    }
}
