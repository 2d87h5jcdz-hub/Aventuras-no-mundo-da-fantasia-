using System;
using UnityEngine;

namespace Joaquim.World
{
    /// <summary>Um mapa em texto. Célula (0,0) é o canto superior esquerdo.</summary>
    public sealed class MapDef
    {
        public string Name { get; }
        public string[] Rows { get; }
        public int Width { get; }
        public int Height { get; }

        public MapDef(string name, string[] rows)
        {
            Name = name;
            Rows = rows;
            Height = rows.Length;
            Width = rows[0].Length;
            foreach (var row in rows)
                if (row.Length != Width)
                    throw new ArgumentException($"Mapa '{name}': todas as linhas precisam ter {Width} caracteres (achei \"{row}\").");
        }

        public bool InBounds(Vector2Int c) => c.x >= 0 && c.y >= 0 && c.x < Width && c.y < Height;

        public char At(Vector2Int c) => InBounds(c) ? Rows[c.y][c.x] : ' ';
    }
}
