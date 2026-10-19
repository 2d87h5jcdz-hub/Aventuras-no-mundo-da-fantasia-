namespace Joaquim.Story
{
    public enum Quem { Narrador, Joaquim, Pai }

    /// <summary>Expressão do retrato na caixa de diálogo (imagens em Art/Retratos).</summary>
    public enum Emocao { Normal, Feliz, Animado, Surpreso, Triste, Chateado, Raiva, Medo }

    public readonly struct Fala
    {
        public readonly Quem Quem;
        public readonly Emocao Emocao;
        public readonly string Texto;
        /// <summary>Mostra o relógio no retrato em vez do rosto de quem fala.</summary>
        public readonly bool MostraRelogio;

        public Fala(Quem quem, Emocao emocao, string texto, bool mostraRelogio = false)
        {
            Quem = quem;
            Emocao = emocao;
            Texto = texto;
            MostraRelogio = mostraRelogio;
        }
    }

    /// <summary>
    /// TODO o texto do jogo fica aqui, separado da lógica.
    /// Quer mudar uma fala ou a expressão do personagem? Edite só este arquivo.
    /// </summary>
    public static class Roteiro
    {
        static Fala J(Emocao e, string t) => new Fala(Quem.Joaquim, e, t);
        static Fala JR(Emocao e, string t) => new Fala(Quem.Joaquim, e, t, mostraRelogio: true);
        static Fala P(Emocao e, string t) => new Fala(Quem.Pai, e, t);
        static Fala N(string t) => new Fala(Quem.Narrador, Emocao.Normal, t);

        const Emocao Normal = Emocao.Normal, Feliz = Emocao.Feliz, Animado = Emocao.Animado,
            Surpreso = Emocao.Surpreso, Triste = Emocao.Triste, Chateado = Emocao.Chateado,
            Raiva = Emocao.Raiva, Medo = Emocao.Medo;

        // ---------------------------------------------------------------- telas

        public const string Titulo = "Joaquim No Reino da Fantasia";
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
            J(Animado, "Ufa, acabou a aula! Hora de voltar pra casa."),
        };

        public static readonly Fala[] ViuBrilho =
        {
            J(Surpreso, "Ué... tem alguma coisa brilhando ali na grama."),
        };

        public static readonly Fala[] AchouRelogio =
        {
            JR(Surpreso, "É um relógio de pulso!"),
            JR(Normal, "Mas ele é diferente... não tem números, só uns símbolos estranhos."),
            JR(Surpreso, "E os ponteiros estão girando ao contrário!"),
            J(Feliz, "Alguém deve ter perdido. Vou levar pra casa e mostrar pro meu pai."),
        };

        public static readonly Fala[] SaidaSemRelogio =
        {
            J(Normal, "Espera... o que é aquele brilho perto da escola?"),
        };

        // ---------------------------------------------------------------- casa

        public static readonly Fala[] ConversaPai =
        {
            P(Feliz, "Oi, filhão! Como foi na escola hoje?"),
            J(Animado, "Foi legal, pai! Olha o que eu achei no gramado da escola."),
            P(Normal, "Deixa eu ver... Que relógio diferente! Nunca vi um desses."),
            P(Normal, "Amanhã a gente leva na escola, pra ver se alguém perdeu. Tá bom?"),
            J(Chateado, "Tá bom..."),
            P(Feliz, "Agora vai pro quarto descansar, que já tá tarde. Boa noite, filho!"),
            J(Feliz, "Boa noite, pai!"),
        };

        public static readonly Fala[] PaiDepois =
        {
            P(Feliz, "Vai descansar, campeão. Amanhã a gente resolve isso."),
        };

        public static readonly Fala[] PortaAntesDoPai =
        {
            J(Normal, "Melhor falar com o pai primeiro."),
        };

        // ---------------------------------------------------------------- quarto

        public static readonly Fala[] QuartoChegada =
        {
            J(Normal, "Que dia..."),
        };

        public static readonly Fala[] NaCama =
        {
            J(Normal, "Quem será que perdeu esse relógio...?"),
            N("Tic... tac... tic... tac..."),
        };

        public static readonly Fala[] RelogioBrilha =
        {
            JR(Medo, "Ué?! O relógio... tá brilhando!"),
        };

        // ---------------------------------------------------------------- floresta

        public static readonly Fala[] Acordou =
        {
            N("..."),
            J(Triste, "Hmm... onde... onde eu estou?"),
        };

        public static readonly Fala[] Levantou =
        {
            J(Surpreso, "Isso é uma floresta?!"),
            J(Medo, "Mas eu tava na minha cama agorinha mesmo..."),
            JR(Normal, "O relógio ainda tá no meu pulso. Os ponteiros não param de girar."),
        };

        public static readonly Fala[] FimCapitulo =
        {
            J(Surpreso, "Tem uma luz lá na frente... será que é a saída?"),
        };
    }
}
