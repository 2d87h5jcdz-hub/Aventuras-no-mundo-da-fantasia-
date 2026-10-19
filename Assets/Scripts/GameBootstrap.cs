using Joaquim.Actors;
using Joaquim.Audio;
using Joaquim.Core;
using Joaquim.Render;
using Joaquim.Story;
using Joaquim.UI;
using Joaquim.World;
using UnityEngine;

namespace Joaquim
{
    /// <summary>
    /// Ponto de partida: monta o jogo inteiro por código assim que a cena carrega.
    /// Por isso a cena pode ser vazia — é só apertar Play.
    /// </summary>
    public static class GameBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Boot()
        {
            if (Object.FindFirstObjectByType<StoryDirector>() != null) return;

            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            QualitySettings.shadows = ShadowQuality.Disable;
            QualitySettings.antiAliasing = 0;

            // Câmera 3D em perspectiva (estilo HD-2D)
            var cam = Camera.main;
            if (cam == null)
            {
                var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
                cam = camGo.AddComponent<Camera>();
            }
            if (cam.GetComponent<AudioListener>() == null) cam.gameObject.AddComponent<AudioListener>();
            cam.orthographic = false;
            cam.fieldOfView = 31f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 120f;
            cam.allowMSAA = false;
            cam.allowHDR = false;

            var post = cam.GetComponent<HD2DPost>();
            if (post == null) post = cam.gameObject.AddComponent<HD2DPost>();

            // Sistemas
            var root = new GameObject("Jogo");
            var world = root.AddComponent<GameWorld>();
            var dialogue = root.AddComponent<DialogueBox>();
            var fader = root.AddComponent<ScreenFader>();
            root.AddComponent<Sfx>();
            root.AddComponent<VirtualStick>();

            var player = new GameObject("Joaquim").AddComponent<Player>();
            player.World = world;
            player.Cam = cam;

            var rig = cam.GetComponent<CameraRig>();
            if (rig == null) rig = cam.gameObject.AddComponent<CameraRig>();
            rig.World = world;
            rig.Target = player.transform;
            rig.Post = post;

            var motes = new GameObject("Partículas").AddComponent<Motes>();
            motes.Follow = player.transform;

            var story = root.AddComponent<StoryDirector>();
            story.Init(world, player, rig, dialogue, fader, motes);
        }
    }
}
