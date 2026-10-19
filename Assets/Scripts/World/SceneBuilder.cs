using Joaquim.Render;
using UnityEngine;

namespace Joaquim.World
{
    /// <summary>
    /// Transforma cada mapa em texto num cenário 3D estilo HD-2D:
    /// chão deitado, paredes/fachadas em pé, e árvores, móveis e objetos como "placas" (billboards).
    /// </summary>
    public static class SceneBuilder
    {
        /// <summary>Tiles extras de chão em volta do mapa (igual a MARGEM em tools/arte/cenarios.py).</summary>
        public const int Margin = 8;

        public static ScenePreset Build(GameWorld world, MapDef map)
        {
            switch (map.Name)
            {
                case "Escola": return Escola(world, map);
                case "Casa": return Interior(world, map, ScenePreset.Casa, "casa");
                case "Quarto": return Interior(world, map, ScenePreset.Quarto, "quarto");
                case "Floresta": return Floresta(world, map);
            }
            Debug.LogWarning("[Joaquim] Mapa sem montagem 3D: " + map.Name);
            return new ScenePreset();
        }

        // ================================================================ peças comuns

        static void Ground(GameWorld w, MapDef map, string tex, Color tint)
        {
            var o = new Vector3(-0.5f - Margin, 0f, 0.5f + Margin);
            var q = Quad.Surface("chão", w.Root, Art.Tex("Cenarios/" + tex), o,
                new Vector3(map.Width + 2 * Margin, 0, 0), new Vector3(0, 0, -(map.Height + 2 * Margin)));
            q.SetColor(tint);
        }

        static void Sky(GameWorld w, string tex)
        {
            var q = Quad.Surface("céu", w.Root, Art.Tex("Cenarios/" + tex), new Vector3(-40f, 34f, 30f),
                new Vector3(110f, 0, 0), new Vector3(0, -40f, 0));
            q.SetNoHaze(true);
        }

        static Quad Prop(GameWorld w, string tex, Vector3 foot, float scale = 1f, float shadow = 0f, bool flip = false)
        {
            var q = Quad.Billboard(tex, w.Root, Art.Tex("Objetos/" + tex), foot, scale);
            q.SetColor(w.Preset.PropTint);
            q.SetFlip(flip);
            if (shadow > 0f) w.SpawnShadow(foot, shadow);
            return q;
        }

        static Vector3 At(int x, int y) => new Vector3(x, 0f, -y);

        /// <summary>Número "aleatório" fixo por posição (o cenário fica igual toda vez).</summary>
        static float Hash(int x, int y, int salt = 0)
        {
            uint h = (uint)(x * 73856093) ^ (uint)(y * 19349663) ^ (uint)(salt * 83492791);
            h ^= h >> 13; h *= 0x5bd1e995; h ^= h >> 15;
            return (h & 0xFFFFFF) / (float)0x1000000;
        }

        // ================================================================ escola

        static ScenePreset Escola(GameWorld w, MapDef map)
        {
            var p = ScenePreset.Escola;
            SetPreset(w, p);
            Ground(w, map, "escola_chao", p.GroundTint);
            Sky(w, "escola_ceu");

            // fachada: a linha do mapa que tem a porta (D)
            int fr = 0;
            for (int y = 0; y < map.Height; y++) if (map.Rows[y].Contains("D")) { fr = y; break; }
            float front = -fr - 0.5f;
            var fachada = Quad.Surface("fachada", w.Root, Art.Tex("Cenarios/escola_fachada"),
                new Vector3(0.5f, 4.5f, front), new Vector3(map.Width - 2, 0, 0), new Vector3(0, -4.5f, 0));
            fachada.SetColor(p.WallTint);
            var telhado = Quad.Surface("telhado", w.Root, Art.Tex("Cenarios/escola_telhado"),
                new Vector3(-0.5f, 6.6f, front + 2.3f), new Vector3(map.Width, 0, 0), new Vector3(0, -2.1f, -2.45f));
            telhado.SetColor(p.WallTint * 1.05f);
            // paredes laterais do prédio (fecham a caixa)
            foreach (float sx in new[] { 0.5f, map.Width - 1.5f })
            {
                var lado = Quad.Surface("lado", w.Root, Art.Tex("Cenarios/escola_fachada"),
                    new Vector3(sx, 4.5f, front + 2.3f), new Vector3(0, 0, -2.3f), new Vector3(0, -4.5f, 0));
                lado.SetColor(p.WallTint * 0.75f);
            }

            for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
            {
                char c = map.Rows[y][x];
                var pos = At(x, y);
                bool frente = y >= map.Height - 1; // última linha: perto da câmera
                switch (c)
                {
                    case 'T':
                        if (y < fr && x > 0 && x < map.Width - 1) break; // atrás do prédio
                        if (frente && x > 2 && x < map.Width - 3)
                            Prop(w, "arbusto" + (int)(Hash(x, y) * 2), pos, 1f, 0.6f);
                        else
                            Prop(w, "arvore" + (int)(Hash(x, y) * 4), pos + Jitter(x, y, 0.2f), 1f, 1.3f, Hash(x, y, 3) > .5f);
                        break;
                    case 'o':
                        Prop(w, "arbusto" + (int)(Hash(x, y) * 2), pos, 1f, 0.6f);
                        break;
                    case 'F':
                        Prop(w, "cerca", pos, 1f);
                        break;
                }
            }
            // arbustos rente à fachada
            for (int x = 2; x < map.Width - 2; x += 3)
                if (map.Rows[fr + 1][x] != ':' && map.Rows[fr + 1][x] != '@')
                    Prop(w, "arbusto" + (x % 2), new Vector3(x, 0, front - 0.25f), 0.9f, 0.5f);

            // poste aceso perto do caminho
            var poste = new Vector2Int(14, fr + 3);
            if (map.InBounds(poste) && !TileLegend.IsSolid(map.At(poste)))
            {
                Prop(w, "poste", At(poste.x, poste.y), 1f, 0.3f);
                w.AddBlocker(poste);
                w.SpawnLight(At(poste.x, poste.y), 1.8f, new Color(1f, 0.75f, 0.4f, 0.55f));
                // a imagem da luz tem 4 tiles; com escala 0.7 o centro fica 1.4 acima do "pé" → na lanterna
                var halo = Quad.Billboard("halo", w.Root, Art.Tex("Efeitos/luz"), At(poste.x, poste.y) + new Vector3(0, 1.2f, -0.05f), 0.7f, QuadStyle.Additive);
                halo.SetColor(new Color(1f, 0.8f, 0.45f, 0.7f));
            }

            MarginTrees(w, map, 0.45f, false);
            return p;
        }

        static Vector3 Jitter(int x, int y, float amount) =>
            new Vector3((Hash(x, y, 11) - .5f) * 2f * amount, 0f, (Hash(x, y, 12) - .5f) * 2f * amount);

        /// <summary>Árvores fora do mapa jogável, para o mundo não "acabar" na borda.</summary>
        static void MarginTrees(GameWorld w, MapDef map, float density, bool mata)
        {
            for (int y = -Margin; y < map.Height + Margin; y++)
            for (int x = -Margin; x < map.Width + Margin; x++)
            {
                if (map.InBounds(new Vector2Int(x, y))) continue;
                bool baixo = y >= map.Height;
                // embaixo (perto da câmera) só nas laterais, pra não tapar a visão
                if (baixo && x > 1 && x < map.Width - 2) continue;
                if (Hash(x, y, 5) > density) continue;
                var pos = At(x, y) + Jitter(x, y, 0.35f);
                string tex = mata ? "arvore_mata" + (int)(Hash(x, y, 6) * 4) : "arvore" + (int)(Hash(x, y, 6) * 4);
                Prop(w, tex, pos, 0.9f + Hash(x, y, 7) * 0.3f, 0f, Hash(x, y, 8) > .5f);
            }
        }

        // ================================================================ interiores

        static ScenePreset Interior(GameWorld w, MapDef map, ScenePreset p, string nome)
        {
            SetPreset(w, p);
            Ground(w, map, nome + "_chao", p.GroundTint);
            const float H = 3f;

            // parede do fundo (linha 0 do mapa já tem janelas, estantes e o vão da porta pintados)
            var fundo = Quad.Surface("parede", w.Root, Art.Tex("Cenarios/" + nome + "_parede"),
                new Vector3(-0.5f, H, -0.5f), new Vector3(map.Width, 0, 0), new Vector3(0, -H, 0));
            fundo.SetColor(p.WallTint);
            foreach (float sx in new[] { -0.5f, map.Width - 0.5f })
            {
                var lado = Quad.Surface("parede lado", w.Root, Art.Tex("Cenarios/" + nome + "_parede_lado"),
                    new Vector3(sx, H, -0.5f), new Vector3(0, 0, -(map.Height - 0.5f)), new Vector3(0, -H, 0));
                lado.SetColor(p.WallTint * 0.8f);
            }

            for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
            {
                char c = map.Rows[y][x];
                var pos = At(x, y);
                switch (c)
                {
                    case 'd':
                        w.Door = Quad.Surface("porta", w.Root, Art.Tex("Cenarios/porta"),
                            new Vector3(x - 0.5f, 2.625f, -0.48f), new Vector3(1, 0, 0), new Vector3(0, -2.625f, 0));
                        w.Door.SetColor(p.WallTint);
                        break;
                    case 'p':
                        Prop(w, "planta", pos, 1f, 0.45f);
                        break;
                    case 's':
                        Prop(w, "poltrona", pos, 1f, 0.6f, x > map.Width / 2);
                        break;
                    case 't':
                        Prop(w, "mesinha", pos, 1f, 0.5f);
                        if (y == FirstRowOf(map, 't'))
                        {
                            w.SpawnLight(pos, 2.4f, new Color(1f, 0.72f, 0.38f, 0.6f));
                            var halo = Quad.Billboard("halo", w.Root, Art.Tex("Efeitos/luz"), pos + new Vector3(0, 0.1f, -0.05f), 0.55f, QuadStyle.Additive);
                            halo.SetColor(new Color(1f, 0.8f, 0.45f, 0.6f));
                        }
                        break;
                    case 'v':
                        Prop(w, "tv", pos, 1f, 0.5f);
                        w.SpawnLight(pos + new Vector3(0, 0, -0.6f), 1.2f, new Color(0.4f, 0.6f, 1f, 0.35f));
                        break;
                    case 'n':
                        // luar entrando pela janela
                        var luar = w.SpawnLight(At(x, 1) + new Vector3(0, 0, -0.4f), 1.4f, new Color(0.55f, 0.65f, 1f, 0.45f));
                        luar.transform.localScale = new Vector3(0.8f, 1f, 1.3f);
                        break;
                    case 'B':
                        Bed(w, map, x, y, p);
                        break;
                }
            }
            return p;
        }

        static int FirstRowOf(MapDef map, char c)
        {
            for (int y = 0; y < map.Height; y++) if (map.Rows[y].IndexOf(c) >= 0) return y;
            return -1;
        }

        /// <summary>Cama em 3D: colchão deitado (cabeceira na célula B, pé na célula E abaixo).</summary>
        static void Bed(GameWorld w, MapDef map, int x, int y, ScenePreset p)
        {
            const float h = 0.5f;
            float z0 = -y + 0.42f, z1 = -(y + 1) - 0.5f;
            w.BedTop = Quad.Surface("cama", w.Root, Art.Tex("Objetos/cama_topo"),
                new Vector3(x - 0.5f, h, z0), new Vector3(1, 0, 0), new Vector3(0, 0, z1 - z0));
            w.BedTop.SetColor(p.PropTint);
            var frente = Quad.Surface("cama frente", w.Root, Art.Tex("Objetos/cama_frente"),
                new Vector3(x - 0.5f, h, z1), new Vector3(1, 0, 0), new Vector3(0, -h, 0));
            frente.SetColor(p.PropTint * 0.85f);
            foreach (float sx in new[] { x - 0.5f, x + 0.5f })
            {
                var lado = Quad.Surface("cama lado", w.Root, Art.Tex("Objetos/cama_frente"),
                    new Vector3(sx, h, z0), new Vector3(0, 0, z1 - z0), new Vector3(0, -h, 0));
                lado.SetColor(p.PropTint * 0.7f);
            }
            var cab = Quad.Billboard("cabeceira", w.Root, Art.Tex("Objetos/cama_cabeceira"), new Vector3(x, 0, z0 + 0.02f));
            cab.SetColor(p.PropTint);
            w.SpawnShadow(new Vector3(x, 0, (z0 + z1) / 2f), 0.9f);
        }

        // ================================================================ floresta

        static ScenePreset Floresta(GameWorld w, MapDef map)
        {
            var p = ScenePreset.Floresta;
            SetPreset(w, p);
            Ground(w, map, "floresta_chao", p.GroundTint);
            Sky(w, "floresta_ceu");

            for (int y = 0; y < map.Height; y++)
            for (int x = 0; x < map.Width; x++)
            {
                char c = map.Rows[y][x];
                var pos = At(x, y);
                bool perto = y >= map.Height - 2; // linhas perto da câmera: nada alto, pra não tapar o Joaquim
                switch (c)
                {
                    case 'C':
                    case 'A':
                    case 'Y':
                        if (perto)
                        {
                            Prop(w, "arbusto" + (int)(Hash(x, y) * 2), pos + Jitter(x, y, 0.3f), 1.1f, 0f, Hash(x, y, 2) > .5f);
                            break;
                        }
                        float s = c == 'C' ? 0.95f + Hash(x, y, 7) * 0.35f : 0.55f + Hash(x, y, 7) * 0.15f;
                        if (c == 'C' && Hash(x, y, 9) < 0.35f) break; // menos árvores = menos peso, a copa cobre
                        Prop(w, "arvore_mata" + (int)(Hash(x, y, 6) * 4), pos + Jitter(x, y, c == 'C' ? 0.4f : 0.15f), s,
                            c == 'C' ? 0f : 1.1f, Hash(x, y, 8) > .5f);
                        break;
                    case ';':
                        for (int k = 0; k < 2; k++)
                            Prop(w, "capim" + k, pos + Jitter(x + k * 31, y, 0.4f), 1f);
                        break;
                    case 'm':
                        Prop(w, "cogumelo", pos, 1f, 0.25f);
                        break;
                    case 'L':
                        Prop(w, "tronco", pos, 1f, 0.8f);
                        break;
                }
            }

            // saída: luz forte entrando pela mata
            var saida = w.FindAll('!');
            if (saida.Count > 0)
            {
                Vector3 c = Vector3.zero;
                foreach (var s in saida) c += At(s.x, s.y);
                c /= saida.Count;
                w.SpawnLight(c, 3f, new Color(1f, 0.95f, 0.75f, 0.8f));
                var feixe = Quad.Billboard("luz da saída", w.Root, Art.Tex("Efeitos/luz"), c + new Vector3(1.2f, -1f, 0.5f), 1.6f, QuadStyle.Additive);
                feixe.SetColor(new Color(1f, 0.95f, 0.8f, 0.9f));
            }

            MarginTrees(w, map, 0.75f, true);
            return p;
        }

        static void SetPreset(GameWorld w, ScenePreset p)
        {
            // Preset precisa estar no GameWorld antes de criar objetos (Prop usa o tom)
            w.Preset = p;
        }
    }
}
