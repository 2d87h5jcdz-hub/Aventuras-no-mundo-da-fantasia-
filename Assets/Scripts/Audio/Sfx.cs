using UnityEngine;

namespace Joaquim.Audio
{
    /// <summary>
    /// Efeitos sonoros "8 bits" gerados por código (sem arquivos de áudio).
    /// Dá pra trocar por .wav de verdade no futuro sem mexer na história.
    /// </summary>
    public sealed class Sfx : MonoBehaviour
    {
        const int Rate = 22050;
        static readonly float[] ChimeNotes = { 523.25f, 659.25f, 783.99f, 1046.5f }; // dó-mi-sol-dó
        static Sfx _i;

        AudioSource _src;
        AudioClip _blip, _chime, _tick, _hum, _step;

        void Awake()
        {
            _i = this;
            _src = gameObject.AddComponent<AudioSource>();
            _src.playOnAwake = false;

            _blip = Make("blip", 0.035f, (t, k) => Square(t * 740f) * 0.5f * (1f - k));
            _tick = Make("tick", 0.05f, (t, k) => Square(t * 1800f) * 0.6f * Mathf.Pow(1f - k, 4f));
            _step = Make("door", 0.12f, (t, k) => Noise() * 0.4f * (1f - k));
            _chime = Make("chime", 0.6f, (t, k) =>
            {
                int n = Mathf.Min(3, (int)(k * 6f));
                float local = k * 6f - n;
                float env = n == 3 ? Mathf.Clamp01(1f - (k - 0.5f) * 2f) : 1f - local * 0.3f;
                return Triangle(t * ChimeNotes[n]) * 0.45f * env;
            });
            _hum = Make("hum", 5f, (t, k) =>
            {
                // zumbido que sobe, com "tremido" — a luz do relógio crescendo
                float phase = 140f * t + (1100f - 140f) * t * k * k / 3f; // integral aproximada
                float trem = 0.65f + 0.35f * Mathf.Sin(t * Mathf.PI * 2f * Mathf.Lerp(3f, 14f, k));
                float env = Mathf.Clamp01(k * 3f) * Mathf.Clamp01((1f - k) * 8f);
                return (Triangle(phase) * 0.6f + Square(phase * 0.5f) * 0.15f) * trem * env * 0.55f;
            });
        }

        delegate float Wave(float t, float k);

        static AudioClip Make(string name, float seconds, Wave wave)
        {
            int n = Mathf.CeilToInt(seconds * Rate);
            var data = new float[n];
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                data[i] = Mathf.Clamp(wave(t, i / (float)n), -1f, 1f);
            }
            var clip = AudioClip.Create(name, n, 1, Rate, false);
            clip.SetData(data, 0);
            return clip;
        }

        static float Square(float cycles) => (cycles - Mathf.Floor(cycles)) < 0.5f ? 1f : -1f;

        static float Triangle(float cycles)
        {
            float f = cycles - Mathf.Floor(cycles);
            return f < 0.5f ? f * 4f - 1f : 3f - f * 4f;
        }

        static float Noise() => Random.value * 2f - 1f;

        static void Play(AudioClip clip, float volume)
        {
            if (_i != null && clip != null) _i._src.PlayOneShot(clip, volume);
        }

        public static void Blip() => Play(_i?._blip, 0.25f);
        public static void Tick() => Play(_i?._tick, 0.5f);
        public static void Chime() => Play(_i?._chime, 0.6f);
        public static void Hum() => Play(_i?._hum, 0.7f);
        public static void Door() => Play(_i?._step, 0.5f);
    }
}
