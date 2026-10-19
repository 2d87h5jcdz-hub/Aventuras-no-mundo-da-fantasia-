using UnityEngine;

namespace Joaquim.Render
{
    /// <summary>
    /// "Clima" visual de cada cenário: câmera, luz, névoa, desfoque, brilho e cor.
    /// Para ajustar o visual de um lugar, mexa nos números daqui.
    /// </summary>
    public sealed class ScenePreset
    {
        // câmera
        public float CamPitch = 15f;       // graus olhando para baixo
        public float CamDistance = 18f;    // distância até o Joaquim
        public float CamFov = 30f;         // abertura vertical (graus)
        public float CamTargetHeight = 1f; // altura do ponto que a câmera mira
        public float CamSidePadding = 2f;  // quanto a câmera pode passar da borda do mapa

        // luz (multiplica a cor das imagens)
        public Color GroundTint = Color.white;
        public Color PropTint = Color.white;
        public Color WallTint = Color.white;
        public Color Background = Color.black;

        // sombras no chão
        public Color ShadowColor = new Color(0.25f, 0.2f, 0.35f, 0.65f);
        public Vector2 ShadowOffset = new Vector2(-0.35f, 0.25f); // para onde a sombra "cai"

        // névoa de distância
        public Color HazeColor = new Color(0.94f, 0.69f, 0.5f);
        public float HazeDensity = 0.03f;
        public float HazeStrength = 0.5f;

        // pós-processamento
        public float DofStrength = 20f;
        public float DofMax = 1f;
        public float BloomThreshold = 0.75f;
        public float BloomIntensity = 0.9f;
        public Color BloomTint = new Color(1f, 0.9f, 0.75f);
        public float Vignette = 0.35f;
        public float Saturation = 1.15f;
        public float Contrast = 1.05f;
        public Color ShadowTint = new Color(0.05f, 0.03f, 0.12f);
        public Color Grade = Color.white;
        public float RaysIntensity;
        public float RaysAngle = -0.5f;
        public Color RaysColor = new Color(1f, 0.78f, 0.5f);

        // partículas flutuando (pólen, poeira, vaga-lumes)
        public int MoteCount = 40;
        public Color MoteColor = new Color(1f, 0.86f, 0.6f, 0.8f);
        public float MoteSize = 0.07f;

        // ------------------------------------------------------------ cenários

        /// <summary>Fim de tarde dourado na escola.</summary>
        public static ScenePreset Escola => new ScenePreset
        {
            GroundTint = new Color(1.0f, 0.9f, 0.76f),
            PropTint = new Color(0.98f, 0.86f, 0.74f),
            WallTint = new Color(1.0f, 0.88f, 0.76f),
            Background = new Color(0.95f, 0.65f, 0.48f),
            RaysIntensity = 0.32f,
            MoteCount = 45,
        };

        /// <summary>Sala de casa à noite, luz quente de abajur.</summary>
        public static ScenePreset Casa => new ScenePreset
        {
            CamPitch = 30f, CamDistance = 11.5f, CamFov = 30f, CamTargetHeight = 0.9f, CamSidePadding = 0f,
            GroundTint = new Color(0.92f, 0.78f, 0.62f),
            PropTint = new Color(0.95f, 0.82f, 0.68f),
            WallTint = new Color(0.9f, 0.78f, 0.66f),
            ShadowColor = new Color(0.2f, 0.12f, 0.12f, 0.6f),
            ShadowOffset = new Vector2(0.15f, 0.2f),
            HazeColor = new Color(0.25f, 0.15f, 0.1f), HazeDensity = 0.02f, HazeStrength = 0.3f,
            DofStrength = 9f,
            BloomThreshold = 0.7f, BloomIntensity = 0.8f,
            Vignette = 0.45f, Saturation = 1.1f,
            Grade = new Color(1.05f, 0.98f, 0.9f),
            MoteCount = 18, MoteColor = new Color(1f, 0.85f, 0.6f, 0.4f), MoteSize = 0.04f,
        };

        /// <summary>Quarto à noite: luar azulado.</summary>
        public static ScenePreset Quarto => new ScenePreset
        {
            CamPitch = 30f, CamDistance = 10.5f, CamFov = 30f, CamTargetHeight = 0.9f, CamSidePadding = 0f,
            GroundTint = new Color(0.5f, 0.56f, 0.82f),
            PropTint = new Color(0.55f, 0.6f, 0.85f),
            WallTint = new Color(0.48f, 0.54f, 0.8f),
            ShadowColor = new Color(0.12f, 0.12f, 0.25f, 0.6f),
            ShadowOffset = new Vector2(0.2f, -0.2f),
            HazeColor = new Color(0.05f, 0.07f, 0.18f), HazeDensity = 0.03f, HazeStrength = 0.4f,
            DofStrength = 9f,
            BloomThreshold = 0.6f, BloomIntensity = 1.1f, BloomTint = new Color(0.8f, 0.9f, 1f),
            Vignette = 0.55f, Saturation = 1.05f,
            ShadowTint = new Color(0.02f, 0.03f, 0.1f),
            Grade = new Color(0.9f, 0.95f, 1.1f),
            MoteCount = 12, MoteColor = new Color(0.7f, 0.8f, 1f, 0.35f), MoteSize = 0.035f,
        };

        /// <summary>Floresta densa e misteriosa, com raios de luz e vaga-lumes.</summary>
        public static ScenePreset Floresta => new ScenePreset
        {
            CamPitch = 24f, CamDistance = 16f,
            GroundTint = new Color(0.82f, 1.0f, 0.9f),
            PropTint = new Color(0.8f, 0.98f, 0.9f),
            WallTint = new Color(0.8f, 0.98f, 0.9f),
            Background = new Color(0.08f, 0.2f, 0.18f),
            ShadowColor = new Color(0.05f, 0.15f, 0.15f, 0.7f),
            ShadowOffset = new Vector2(-0.15f, 0.3f),
            HazeColor = new Color(0.32f, 0.58f, 0.54f), HazeDensity = 0.045f, HazeStrength = 0.6f,
            DofStrength = 22f,
            BloomThreshold = 0.68f, BloomIntensity = 1.0f, BloomTint = new Color(0.85f, 1f, 0.85f),
            Vignette = 0.6f, Saturation = 1.12f,
            ShadowTint = new Color(0.0f, 0.05f, 0.08f),
            Grade = new Color(0.95f, 1.05f, 1.0f),
            RaysIntensity = 0.45f, RaysAngle = -0.9f, RaysColor = new Color(0.85f, 1f, 0.8f),
            MoteCount = 55, MoteColor = new Color(0.85f, 1f, 0.45f, 0.95f), MoteSize = 0.06f,
        };
    }
}
