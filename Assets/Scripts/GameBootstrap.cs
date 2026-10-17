using Joaquim.Actors;
using Joaquim.Audio;
using Joaquim.Core;
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

            // Câmera
            var cam = Camera.main;
            if (cam == null)
            {
                var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
                cam = camGo.AddComponent<Camera>();
            }
            if (cam.GetComponent<AudioListener>() == null) cam.gameObject.AddComponent<AudioListener>();
            cam.orthographic = true;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 100f;
            cam.allowMSAA = false;
            cam.transform.SetPositionAndRotation(new Vector3(0f, 0f, -10f), Quaternion.identity);

            // Sistemas
            var root = new GameObject("Jogo");
            var world = root.AddComponent<GameWorld>();
            var dialogue = root.AddComponent<DialogueBox>();
            var fader = root.AddComponent<ScreenFader>();
            root.AddComponent<Sfx>();

            var player = new GameObject("Joaquim").AddComponent<Player>();
            player.World = world;
            player.Cam = cam;

            var rig = cam.GetComponent<CameraRig>();
            if (rig == null) rig = cam.gameObject.AddComponent<CameraRig>();
            rig.World = world;
            rig.Target = player.transform;

            var story = root.AddComponent<StoryDirector>();
            story.Init(world, player, rig, dialogue, fader);
        }
    }
}
