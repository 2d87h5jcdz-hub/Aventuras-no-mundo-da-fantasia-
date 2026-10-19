namespace Joaquim.World
{
    /// <summary>O que cada caractere dos mapas significa para a jogabilidade (dá pra andar ou não).
    /// O visual de cada caractere é montado em SceneBuilder.</summary>
    public static class TileLegend
    {
        /// <summary>Caracteres que só marcam algo (personagem, gatilho) e ficam em chão livre.</summary>
        public static bool IsMarker(char c) => c == '@' || c == 'P' || c == '*' || c == 'X' || c == '!';

        public static bool IsSolid(char c)
        {
            switch (c)
            {
                // escola
                case 'T': case 'o': case 'R': case '^': case 'W': case 'w': case 'D': case 'F':
                // casa / quarto
                case '#': case 'n': case 'k': case 'p': case 't': case 's': case 'v': case 'B': case 'E':
                // floresta
                case 'A': case 'Y': case 'C': case 'L':
                case ' ':
                    return true;
                default:
                    return false;
            }
        }
    }
}
