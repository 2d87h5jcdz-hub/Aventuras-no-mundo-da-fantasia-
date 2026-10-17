using Joaquim.Art;
using UnityEngine;

namespace Joaquim.Actors
{
    /// <summary>Troca os quadros de um SpriteRenderer em sequência (null = esconde naquele quadro).</summary>
    public sealed class FrameAnimator : MonoBehaviour
    {
        string[][] _frames;
        float[] _durations;
        SpriteRenderer _sr;
        int _index;
        float _timer;

        public void Play(string[][] frames, float[] durations)
        {
            _frames = frames;
            _durations = durations;
            _sr = GetComponent<SpriteRenderer>();
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
            var art = _frames[_index];
            _sr.enabled = art != null;
            if (art != null) _sr.sprite = SpriteFactory.Get(art);
        }
    }
}
