namespace Joaquim.Story
{
    public enum Quem { Narrador, Joaquim, Pai }

    public readonly struct Fala
    {
        public readonly Quem Quem;
        public readonly string Texto;
        /// <summary>Mostra o relógio no retrato em vez do rosto de quem fala.</summary>
        public readonly bool MostraRelogio;

        public Fala(Quem quem, string texto, bool mostraRelogio = false)
        {
            Quem = quem;
            Texto = texto;
            MostraRelogio = mostraRelogio;
        }
    }

    /// <summary>
    /// TODO o texto do jogo fica aqui, separado da lógica.
    /// Quer mudar uma fala? Edite só este arquivo.
    /// </summary>
    public static class Roteiro
    {
        static Fala J(string t) => new Fala(Quem.Joaquim, t);
        static Fala JR(string t) => new Fala(Quem.Joaquim, t, mostraRelogio: true);
        static Fala P(string t) => new Fala(Quem.Pai, t);
        static Fala N(string t) => new Fala(Quem.Narrador, t);

        // ---------------------------------------------------------------- telas

        public const string Titulo = "Joaquim e o Relógio de Luz";
        public const string TocarParaComecar = "Toque para começar";
        public const string Capitulo1 = "Capítulo 1";
        public const string Capitulo1Nome = "O relógio";
        public const string LegendaCasa = "Em casa...";
        public const string LegendaNoite = "Mais tarde, no quarto...";
        public const string FimTitulo = "Fim do Capítulo 1";
        public const string FimSubtitulo = "Continua...";
        public const string JogarDeNovo = "Toque para jogar de novo";

        // ---------------------------------------------------------------- escola

        public static readonly Fala[] EscolaInicio =
        {
            J("Ufa, acabou a aula! Hora de voltar pra casa."),
        };

        public static readonly Fala[] ViuBrilho =
        {
            J("Ué... tem alguma coisa brilhando ali na grama."),
        };

        public static readonly Fala[] AchouRelogio =
        {
            JR("É um relógio de pulso!"),
            JR("Mas ele é diferente... não tem números, só uns símbolos estranhos."),
            JR("E os ponteiros estão girando ao contrário!"),
            J("Alguém deve ter perdido. Vou levar pra casa e mostrar pro meu pai."),
        };

        public static readonly Fala[] SaidaSemRelogio =
        {
            J("Espera... o que é aquele brilho perto da escola?"),
        };

        // ---------------------------------------------------------------- casa

        public static readonly Fala[] ConversaPai =
        {
            P("Oi, filhão! Como foi na escola hoje?"),
            J("Foi legal, pai! Olha o que eu achei no gramado da escola."),
            P("Deixa eu ver... Que relógio diferente! Nunca vi um desses."),
            P("Amanhã a gente leva na escola, pra ver se alguém perdeu. Tá bom?"),
            J("Tá bom..."),
            P("Agora vai pro quarto descansar, que já tá tarde. Boa noite, filho!"),
            J("Boa noite, pai!"),
        };

        public static readonly Fala[] PaiDepois =
        {
            P("Vai descansar, campeão. Amanhã a gente resolve isso."),
        };

        public static readonly Fala[] PortaAntesDoPai =
        {
            J("Melhor falar com o pai primeiro."),
        };

        // ---------------------------------------------------------------- quarto

        public static readonly Fala[] QuartoChegada =
        {
            J("Que dia..."),
        };

        public static readonly Fala[] NaCama =
        {
            J("Quem será que perdeu esse relógio...?"),
            N("Tic... tac... tic... tac..."),
        };

        public static readonly Fala[] RelogioBrilha =
        {
            JR("Ué?! O relógio... tá brilhando!"),
        };

        // ---------------------------------------------------------------- floresta

        public static readonly Fala[] Acordou =
        {
            N("..."),
            J("Hmm... onde... onde eu estou?"),
        };

        public static readonly Fala[] Levantou =
        {
            J("Isso é uma floresta?!"),
            J("Mas eu tava na minha cama agorinha mesmo..."),
            JR("O relógio ainda tá no meu pulso. Os ponteiros não param de girar."),
        };

        public static readonly Fala[] FimCapitulo =
        {
            J("Tem uma luz lá na frente... será que é a saída?"),
        };
    }
}
