using Joaquim.Art;
using UnityEngine;

namespace Joaquim.World
{
    /// <summary>Diz qual desenho e se dá pra andar em cada caractere dos mapas.</summary>
    public static class TileLegend
    {
        public readonly struct TileInfo
        {
            public readonly string[] Art;
            public readonly bool Solid;
            public TileInfo(string[] art, bool solid) { Art = art; Solid = solid; }
        }

        /// <summary>Caracteres que só marcam algo (personagem, gatilho) e precisam de um chão por baixo.</summary>
        public static bool IsMarker(char c) => c == '@' || c == 'P' || c == '*' || c == 'X' || c == '!';

        static string[] Pick(int x, int y, params string[][] variants)
        {
            // Variação estável por posição, pra grama não parecer "carimbada"
            int h = (x * 73856093) ^ (y * 19349663);
            h = (h ^ (h >> 13)) & 0x7fffffff;
            return variants[h % variants.Length];
        }

        public static bool TryGet(char c, int x, int y, out TileInfo info)
        {
            switch (c)
            {
                // ---- escola (lado de fora)
                case '.': info = new TileInfo(Pick(x, y, PixelArtData.Grass0, PixelArtData.Grass1, PixelArtData.Grass2), false); return true;
                case ',': info = new TileInfo(Pick(x, y, PixelArtData.Flowers0, PixelArtData.Flowers1), false); return true;
                case ':': info = new TileInfo(Pick(x, y, PixelArtData.Dirt0, PixelArtData.Dirt1), false); return true;
                case 'T': info = new TileInfo(PixelArtData.Tree, true); return true;
                case 'o': info = new TileInfo(PixelArtData.Bush, true); return true;
                case 'R': info = new TileInfo(PixelArtData.Roof, true); return true;
                case '^': info = new TileInfo(PixelArtData.RoofEdge, true); return true;
                case 'W': info = new TileInfo(PixelArtData.SchoolWall, true); return true;
                case 'w': info = new TileInfo(PixelArtData.SchoolWindow, true); return true;
                case 'D': info = new TileInfo(PixelArtData.SchoolDoor, true); return true;
                case 'F': info = new TileInfo(PixelArtData.Fence, true); return true;

                // ---- casa
                case '_': info = new TileInfo(Pick(x, y, PixelArtData.Floor0, PixelArtData.Floor1), false); return true;
                case '#': info = new TileInfo(PixelArtData.Wall, true); return true;
                case 'n': info = new TileInfo(PixelArtData.WindowNight, true); return true;
                case 'd': info = new TileInfo(PixelArtData.Door, false); return true;
                case 'k': info = new TileInfo(PixelArtData.Bookshelf, true); return true;
                case 'p': info = new TileInfo(PixelArtData.Plant, true); return true;
                case 't': info = new TileInfo(PixelArtData.Table, true); return true;
                case 's': info = new TileInfo(PixelArtData.Sofa, true); return true;
                case 'v': info = new TileInfo(PixelArtData.Tv, true); return true;
                case 'r': info = new TileInfo(PixelArtData.Rug, false); return true;
                case 'B': info = new TileInfo(PixelArtData.BedHead, true); return true;
                case 'E': info = new TileInfo(PixelArtData.BedFoot, true); return true;

                // ---- floresta
                case '-': info = new TileInfo(Pick(x, y, PixelArtData.ForestFloor0, PixelArtData.ForestFloor1, PixelArtData.ForestFloor2), false); return true;
                case ';': info = new TileInfo(Pick(x, y, PixelArtData.TallGrass0, PixelArtData.TallGrass1), false); return true;
                case 'A': info = new TileInfo(PixelArtData.ForestTree0, true); return true;
                case 'Y': info = new TileInfo(PixelArtData.ForestTree1, true); return true;
                case 'C': info = new TileInfo(Pick(x, y, PixelArtData.Canopy0, PixelArtData.Canopy1), true); return true;
                case 'm': info = new TileInfo(PixelArtData.Mushroom, false); return true;
                case 'L': info = new TileInfo(PixelArtData.Log, true); return true;
            }
            info = default;
            return false;
        }

        /// <summary>Para marcadores (@, P, *...), escolhe o chão olhando os vizinhos.</summary>
        public static char GroundUnder(MapDef map, Vector2Int cell)
        {
            Vector2Int[] dirs = { Vector2Int.left, Vector2Int.right, Vector2Int.down, Vector2Int.up };
            foreach (var d in dirs)
            {
                char n = map.At(cell + d);
                if (!IsMarker(n) && n != 'd' && n != 'm' && TryGet(n, 0, 0, out var info) && !info.Solid) return n;
            }
            return map.Name == "Floresta" ? '-' : map.Name == "Escola" ? '.' : '_';
        }
    }
}
