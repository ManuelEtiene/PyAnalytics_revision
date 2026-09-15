import csv
import re
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

NOME_BAIRRO = "Bom Pastor"

ARQUIVO_ENTRADA = Path(
    "data/bruto/vacinas/"
    "Vacinas_Aplicadas_Bom_Pastor_Anonimizadas.csv"
)

ARQUIVO_SAIDA = Path(
    "data/processed/vacinas/"
    "bom_pastor.csv"
)

COLUNAS_SAIDA = [
    "Nome do bairro",
    "Nome da vacina",
    "Código da vacina",
    "Estratégia",
    "Código da estratégia",
    "Dose",
    "Código da dose",
    "Vacina estratégia e dose",
    "Lote",
    "Validade do lote",
    "Data da aplicação",
    "Origem",
]


# ============================================================
# EXTRAÇÃO DA VACINA
# ============================================================

def extrair_vacina(descricao):
    """
    Extrai os dados disponíveis da descrição.

    Aceita registros completos e incompletos sem inventar dados.
    """

    descricao = descricao.strip()

    padrao = re.match(
        r"^(.+?)\s*\((\d+)\)\s*-\s*"
        r"(.+?)\s*\((\d+)\)\s*-\s*(.*)$",
        descricao
    )

    if not padrao:
        return None

    (
        nome_vacina,
        codigo_vacina,
        estrategia,
        codigo_estrategia,
        dose
    ) = padrao.groups()

    nome_vacina = nome_vacina.strip()
    codigo_vacina = codigo_vacina.strip()
    estrategia = estrategia.strip()
    codigo_estrategia = codigo_estrategia.strip()
    dose = dose.strip()

    # --------------------------------------------------------
    # Sem dose
    # --------------------------------------------------------

    if not dose:
        return {
            "Nome da vacina": nome_vacina,
            "Código da vacina": codigo_vacina,
            "Estratégia": estrategia,
            "Código da estratégia": codigo_estrategia,
            "Dose": "",
            "Código da dose": "",
        }

    # --------------------------------------------------------
    # Dose com código
    # --------------------------------------------------------

    padrao_dose = re.match(
        r"^(.+?)\s*\((\d+)\)$",
        dose
    )

    if padrao_dose:

        nome_dose = padrao_dose.group(1).strip()
        codigo_dose = padrao_dose.group(2).strip()

    else:

        # A dose existe, mas seu código não está na origem
        nome_dose = dose
        codigo_dose = ""

    return {
        "Nome da vacina": nome_vacina,
        "Código da vacina": codigo_vacina,
        "Estratégia": estrategia,
        "Código da estratégia": codigo_estrategia,
        "Dose": nome_dose,
        "Código da dose": codigo_dose,
    }


# ============================================================
# EXTRAÇÃO DO LOTE E VALIDADE
# ============================================================

def extrair_lote_validade(texto):

    texto = texto.strip()

    if not texto:
        return "", ""

    if " - " not in texto:
        return texto, ""

    lote, validade = texto.rsplit(" - ", 1)

    return lote.strip(), validade.strip()


# ============================================================
# IDENTIFICAÇÃO DO CABEÇALHO
# ============================================================

def obter_indices_cabecalho(linha):
    """
    O G-MUS pode mudar a posição das células entre páginas.

    Por isso encontramos as posições através do cabeçalho
    de cada página.
    """

    nomes_necessarios = [
        "Paciente",
        "Vacina, Estratégia e Dose",
        "Lote e Data de Validade",
        "Aplicado",
        "Qtde.",
        "Origem",
    ]

    for nome in nomes_necessarios:
        if nome not in linha:
            return None

    return {
        "paciente": linha.index("Paciente"),
        "vacina": linha.index(
            "Vacina, Estratégia e Dose"
        ),
        "lote": linha.index(
            "Lote e Data de Validade"
        ),
        "aplicado": linha.index("Aplicado"),
        "quantidade": linha.index("Qtde."),
        "origem": linha.index("Origem"),
    }


# ============================================================
# PROCESSAMENTO
# ============================================================

def processar_arquivo():

    registros = []
    registros_ignorados = 0
    linhas_problematicas = []

    indices = None

    with open(
        ARQUIVO_ENTRADA,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        leitor = csv.reader(arquivo)

        for numero_linha, linha in enumerate(
            leitor,
            start=1
        ):

            # ------------------------------------------------
            # Detecta novo cabeçalho
            # ------------------------------------------------

            novo_cabecalho = obter_indices_cabecalho(
                linha
            )

            if novo_cabecalho is not None:

                indices = novo_cabecalho
                continue

            # Ainda não encontramos cabeçalho
            if indices is None:
                continue

            # ------------------------------------------------
            # Verifica tamanho da linha
            # ------------------------------------------------

            maior_indice = max(
                indices.values()
            )

            if len(linha) <= maior_indice:
                continue

            # ------------------------------------------------
            # Extrai campos
            # ------------------------------------------------

            paciente = linha[
                indices["paciente"]
            ].strip()

            descricao = linha[
                indices["vacina"]
            ].strip()

            lote_validade = linha[
                indices["lote"]
            ].strip()

            data_aplicacao = linha[
                indices["aplicado"]
            ].strip()

            origem = linha[
                indices["origem"]
            ].strip()

            # ------------------------------------------------
            # Ignora linhas que não são aplicações
            # ------------------------------------------------

            if not paciente or paciente == "Paciente":
                continue

            if not descricao:
                continue

            # ------------------------------------------------
            # Extrai vacina
            # ------------------------------------------------

            dados_vacina = extrair_vacina(
                descricao
            )

            if dados_vacina is None:

                registros_ignorados += 1

                linhas_problematicas.append(
                    (
                        numero_linha,
                        descricao
                    )
                )

                continue

            # ------------------------------------------------
            # Extrai lote e validade
            # ------------------------------------------------

            lote, validade = extrair_lote_validade(
                lote_validade
            )

            # ------------------------------------------------
            # Cria registro
            # ------------------------------------------------

            registro = {
                "Nome do bairro": NOME_BAIRRO,
                "Nome da vacina":
                    dados_vacina["Nome da vacina"],
                "Código da vacina":
                    dados_vacina["Código da vacina"],
                "Estratégia":
                    dados_vacina["Estratégia"],
                "Código da estratégia":
                    dados_vacina["Código da estratégia"],
                "Dose":
                    dados_vacina["Dose"],
                "Código da dose":
                    dados_vacina["Código da dose"],
                "Vacina estratégia e dose":
                    descricao,
                "Lote":
                    lote,
                "Validade do lote":
                    validade,
                "Data da aplicação":
                    data_aplicacao,
                "Origem":
                    origem,
            }

            registros.append(registro)

    return (
        registros,
        registros_ignorados,
        linhas_problematicas
    )


# ============================================================
# SALVAR CSV
# ============================================================

def salvar_csv(registros):

    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ARQUIVO_SAIDA,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS_SAIDA
        )

        escritor.writeheader()
        escritor.writerows(registros)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print("LIMPEZA - BOM PASTOR")
    print("=" * 60)

    # --------------------------------------------------------
    # Verifica arquivo
    # --------------------------------------------------------

    if not ARQUIVO_ENTRADA.exists():

        print()
        print("ERRO: arquivo de entrada não encontrado.")
        print(
            f"Arquivo esperado: {ARQUIVO_ENTRADA}"
        )

        return

    # --------------------------------------------------------
    # Processa
    # --------------------------------------------------------

    (
        registros,
        registros_ignorados,
        linhas_problematicas
    ) = processar_arquivo()

    # --------------------------------------------------------
    # Salva
    # --------------------------------------------------------

    salvar_csv(registros)

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    print()
    print(
        f"Registros gravados: {len(registros)}"
    )

    print(
        f"Registros não interpretados: "
        f"{registros_ignorados}"
    )

    print(
        f"Arquivo gerado: {ARQUIVO_SAIDA}"
    )

    # --------------------------------------------------------
    # Mostra problemas
    # --------------------------------------------------------

    if linhas_problematicas:

        print()
        print(
            "REGISTROS QUE PRECISAM DE REVISÃO:"
        )

        for numero, descricao in linhas_problematicas:

            print(
                f"Linha {numero}: {descricao}"
            )

    else:

        print()
        print(
            "Todos os registros de vacina foram "
            "interpretados com sucesso."
        )

    print()
    print("Processamento concluído!")


if __name__ == "__main__":
    main()