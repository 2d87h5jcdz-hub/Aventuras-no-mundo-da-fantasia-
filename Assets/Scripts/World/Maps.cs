namespace Joaquim.World
{
    /// <summary>
    /// Os mapas do jogo, desenhados em texto. Cada caractere é um tile (veja TileLegend).
    /// Para mudar um cenário, é só editar as linhas — todas precisam ter o mesmo tamanho.
    ///
    /// Caracteres especiais:
    ///   @  onde o Joaquim aparece      P  o pai
    ///   *  o relógio brilhando         X  saída (gatilho ao pisar)
    ///   !  gatilho de história         d  porta (gatilho ao pisar)
    ///   B/E cama (cabeceira/pé)
    /// </summary>
    public static class Maps
    {
        public static readonly MapDef Escola = new MapDef("Escola", new[]
        {
            "TTTTTTTTTTTTTTTTTTTTTTTT",
            "TRRRRRRRRRRRRRRRRRRRRRRT",
            "T^^^^^^^^^^^^^^^^^^^^^^T",
            "TWwWWwWWwWWDDWWwWWwWWwWT",
            "To..,......@:........,oT",
            "T.,........::......*...T",
            "T....,.....::...,......T",
            "TFFFFFFFFFF::FFFFFFFFFFT",
            "T.T.,...o..::..,.T..o..T",
            "T,....T....::...T.....,T",
            "TTTTTTTTTTTXXTTTTTTTTTTT",
        });

        public static readonly MapDef Casa = new MapDef("Casa", new[]
        {
            "#n##kk#d##n#",
            "p__________p",
            "_s_rrrr__t__",
            "_s_rrrr__t_v",
            "___rrrr_P___",
            "____________",
            "_____@______",
            "____________",
        });

        public static readonly MapDef Quarto = new MapDef("Quarto", new[]
        {
            "##n##k#n##",
            "p______B__",
            "__rrr__E__",
            "__rrr_____",
            "_@________",
            "__________",
        });

        public static readonly MapDef Floresta = new MapDef("Floresta", new[]
        {
            "CCCCCCCCCCCCCCCCCCCCCCCCCC",
            "CCCCACCCYCCCACCCCYCCCACCCC",
            "CCA--;-AY--;--A---Y-;-ACCC",
            "CY-;----;--m----;-----YCCC",
            "CA--m-A--;---YA--;--A--YCC",
            "CC-;--Y-----;-----m-----CC",
            "CA-----;--L----A-;-----!!C",
            "C-@-;------;--Y-----;--!!C",
            "CA-----Y--;----;---A---!!C",
            "CC-;-m----A-----;--m--YCCC",
            "CY--A--;----Y--;----A-;YCC",
            "CCA-;---m--A---;--Y----ACC",
            "CCCYA--;-YCC--A-;-YACCACCC",
            "CCCCCCACCCCCCYCCCCCCACCCCC",
            "CCCCCCCCCCCCCCCCCCCCCCCCCC",
        });
    }
}
