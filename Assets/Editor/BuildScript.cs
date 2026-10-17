using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Joaquim.EditorTools
{
    /// <summary>
    /// Build usado pelo GitHub Actions (GameCI) e também pelo menu "Joaquim" no editor.
    /// Cria a cena principal (vazia — o jogo se monta por código), aplica as configurações
    /// do app e gera o APK (Android) ou o projeto Xcode (iOS).
    /// </summary>
    public static class BuildScript
    {
        public const string ScenePath = "Assets/Scenes/Main.unity";
        const string ProductName = "Joaquim e o Relógio de Luz";
        const string CompanyName = "Joaquim Games";
        const string AppId = "com.joaquimgames.relogiodeluz";

        [MenuItem("Joaquim/Criar cena principal")]
        public static void EnsureMainScene()
        {
            if (!File.Exists(ScenePath))
            {
                Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
                AssetDatabase.Refresh();
            }
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }

        [MenuItem("Joaquim/Aplicar configurações do app")]
        public static void ApplyPlayerSettings() => ApplyPlayerSettings("0.1.0", 1);

        static void ApplyPlayerSettings(string version, int buildNumber)
        {
            PlayerSettings.productName = ProductName;
            PlayerSettings.companyName = CompanyName;
            PlayerSettings.bundleVersion = version;

            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, AppId);
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, AppId);

            // Jogo deitado (paisagem), girando entre as duas posições
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.AutoRotation;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;

            // Android: IL2CPP + ARM 64 bits (vários celulares novos só rodam 64 bits)
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.Android.bundleVersionCode = Math.Max(1, buildNumber);

            PlayerSettings.iOS.buildNumber = Math.Max(1, buildNumber).ToString();
        }

        /// <summary>Chamado pelo GameCI: -executeMethod Joaquim.EditorTools.BuildScript.BuildFromCommandLine</summary>
        public static void BuildFromCommandLine()
        {
            var args = ParseArgs();
            if (!args.TryGetValue("buildTarget", out var targetName))
            {
                Console.WriteLine("[Joaquim] Faltou -buildTarget");
                EditorApplication.Exit(110);
                return;
            }

            var target = (BuildTarget)Enum.Parse(typeof(BuildTarget), targetName, true);
            int runNumber = args.TryGetValue("runNumber", out var rn) && int.TryParse(rn, out var n) ? n : 1;
            string version = "0.1." + runNumber;

            string location = args.TryGetValue("customBuildPath", out var custom) && !string.IsNullOrEmpty(custom)
                ? custom
                : DefaultLocation(target);

            EnsureMainScene();
            ApplyPlayerSettings(version, runNumber);
            if (target == BuildTarget.Android) EditorUserBuildSettings.buildAppBundle = false; // APK, não AAB

            Console.WriteLine($"[Joaquim] Build {target} v{version} -> {location}");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = location,
                target = target,
                targetGroup = BuildPipeline.GetBuildTargetGroup(target),
                options = BuildOptions.None
            });

            var summary = report.summary;
            Console.WriteLine($"[Joaquim] Resultado: {summary.result}, erros: {summary.totalErrors}, tamanho: {summary.totalSize} bytes");
            EditorApplication.Exit(summary.result == BuildResult.Succeeded ? 0 : 101);
        }

        static string DefaultLocation(BuildTarget target)
        {
            switch (target)
            {
                case BuildTarget.Android: return "build/Android/Joaquim.apk";
                case BuildTarget.iOS: return "build/iOS/Joaquim";
                default: return "build/" + target + "/Joaquim";
            }
        }

        static Dictionary<string, string> ParseArgs()
        {
            var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            var argv = Environment.GetCommandLineArgs();
            for (int i = 0; i < argv.Length; i++)
            {
                if (!argv[i].StartsWith("-")) continue;
                string key = argv[i].TrimStart('-');
                string value = i + 1 < argv.Length && !argv[i + 1].StartsWith("-") ? argv[i + 1] : "";
                result[key] = value;
            }
            return result;
        }
    }

    /// <summary>Ao abrir o projeto no editor, garante que a cena principal existe e já a abre.</summary>
    [InitializeOnLoad]
    static class FirstOpenSetup
    {
        static FirstOpenSetup()
        {
            if (Application.isBatchMode) return;
            EditorApplication.delayCall += () =>
            {
                if (File.Exists(BuildScript.ScenePath)) return;
                BuildScript.EnsureMainScene();
                BuildScript.ApplyPlayerSettings();
                EditorSceneManager.OpenScene(BuildScript.ScenePath);
                Debug.Log("[Joaquim] Cena principal criada em " + BuildScript.ScenePath + ". É só apertar Play!");
            };
        }
    }
}
