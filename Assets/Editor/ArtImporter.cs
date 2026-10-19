using UnityEditor;
using UnityEngine;

namespace Joaquim.EditorTools
{
    /// <summary>
    /// Configura automaticamente as imagens de Assets/Resources/Art ao importar:
    /// pixel art nítida (sem suavizar, sem compressão). Efeitos (luz/sombra) ficam suaves.
    /// </summary>
    public sealed class ArtImporter : AssetPostprocessor
    {
        // aumente quando mudar as regras abaixo, para a Unity reimportar as imagens
        public override uint GetVersion() => 1;

        void OnPreprocessTexture()
        {
            if (!assetPath.Replace('\\', '/').Contains("/Resources/Art/")) return;
            var ti = (TextureImporter)assetImporter;
            bool efeito = assetPath.Contains("/Efeitos/");
            bool ceu = assetPath.Contains("_ceu");

            ti.textureType = TextureImporterType.Default;
            ti.alphaSource = TextureImporterAlphaSource.FromInput;
            ti.alphaIsTransparency = true;
            ti.mipmapEnabled = false;
            ti.npotScale = TextureImporterNPOTScale.None;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.filterMode = efeito || ceu ? FilterMode.Bilinear : FilterMode.Point;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            ti.isReadable = false;
            ti.maxTextureSize = 2048;
        }
    }
}
