using System.Collections;
using System.IO;
using Joaquim.Core;
using UnityEngine;
using UnityEngine.Video;

namespace Joaquim.UI
{
    /// <summary>
    /// Toca o vídeo de abertura (Assets/StreamingAssets/abertura.mp4) em tela cheia.
    /// Um toque pula. Se o vídeo não existir ou der erro, segue direto para o jogo.
    /// </summary>
    public sealed class IntroVideo : MonoBehaviour
    {
        public const string FileName = "abertura.mp4";

        VideoPlayer _player;
        RenderTexture _target;
        bool _showing;
        bool _failed;
        float _startTime;
        GUIStyle _hint;

        public IEnumerator Play()
        {
            string url = Path.Combine(Application.streamingAssetsPath, FileName);
#if UNITY_EDITOR || UNITY_IOS || UNITY_STANDALONE
            if (!File.Exists(url))
            {
                Debug.Log("[Joaquim] Sem vídeo de abertura em " + url);
                yield break;
            }
#endif
            _target = new RenderTexture(960, 540, 0) { filterMode = FilterMode.Bilinear };
            _player = gameObject.AddComponent<VideoPlayer>();
            _player.playOnAwake = false;
            _player.source = VideoSource.Url;
            _player.url = url;
            _player.renderMode = VideoRenderMode.RenderTexture;
            _player.targetTexture = _target;
            _player.audioOutputMode = VideoAudioOutputMode.Direct;
            _player.isLooping = false;
            _player.skipOnDrop = true;
            _player.errorReceived += (p, msg) =>
            {
                Debug.LogWarning("[Joaquim] Erro no vídeo de abertura: " + msg);
                _failed = true;
            };

            _player.Prepare();
            float wait = 0f;
            while (!_player.isPrepared && !_failed && wait < 8f)
            {
                wait += Time.unscaledDeltaTime;
                yield return null;
            }
            if (_failed || !_player.isPrepared)
            {
                Cleanup();
                yield break;
            }

            _player.Play();
            _showing = true;
            _startTime = Time.unscaledTime;
            yield return null;

            bool ended = false;
            _player.loopPointReached += p => ended = true;
            while (!ended && !_failed)
            {
                if (Time.unscaledTime - _startTime > 0.5f && InputBridge.AnyConfirm())
                {
                    InputBridge.Consume();
                    break;
                }
                yield return null;
            }
            Cleanup();
        }

        void Cleanup()
        {
            _showing = false;
            if (_player != null)
            {
                _player.Stop();
                Destroy(_player);
                _player = null;
            }
            if (_target != null)
            {
                _target.Release();
                Destroy(_target);
                _target = null;
            }
        }

        void OnGUI()
        {
            if (!_showing || _target == null) return;
            GUI.depth = -30;
            var full = new Rect(0, 0, Screen.width, Screen.height);
            PixelGui.Fill(full, Color.black);
            GUI.DrawTexture(full, _target, ScaleMode.ScaleToFit);

            // dica discreta para pular (aparece depois de 2 s e some aos 7 s)
            float t = Time.unscaledTime - _startTime;
            float a = Mathf.Clamp01((t - 2f) * 2f) * Mathf.Clamp01((7f - t) * 2f);
            if (a <= 0f) return;
            if (_hint == null)
                _hint = PixelGui.Label(Mathf.Max(12, Screen.height / 34), TextAnchor.LowerRight, Color.white);
            var safe = PixelGui.SafeArea;
            float m = Screen.height * 0.03f;
            _hint.normal.textColor = new Color(1f, 1f, 1f, 0.7f * a);
            GUI.Label(new Rect(safe.x, safe.y, safe.width - m, safe.height - m), "Toque para pular", _hint);
        }
    }
}
