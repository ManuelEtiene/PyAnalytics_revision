import csv
import re
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

NOME_BAIRRO = "Vila São José"

ARQUIVO_ENTRADA = Path(
    "data/bruto/vacinas/"
    "Vacinas_Aplicadas_Vila_Sao_Jose_Anonimizadas.csv"
)

ARQUIVO_SAIDA = Path(
    "data/processed/vacinas/"
    "vila_sao_jose.csv"
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
# EXTRAIR DADOS DA VACINA
# ============================================================

def extrair_vacina(descricao):
    """
    Extrai:

    Nome da vacina
    Código da vacina
    Estratégia
    Código da estratégia
    Dose
    Código da dose

    Aceita registros completos ou incompletos.
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

        # Existe a descrição da dose,
        # mas não existe o código.
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
# EXTRAIR DOSE ISOLADA
# ============================================================

def extrair_dose_isolada(descricao):
    """
    Identifica somente uma linha que possui uma dose.

    Exemplo válido:

    3ª DOSE (3)

    NÃO deve interpretar:

    Vacina polio (...) (22) - Rotina (1) - 3ª DOSE (3)

    como dose isolada.
    """

    descricao = descricao.strip()

    # Uma dose isolada NÃO possui " - "
    if " - " in descricao:
        return None

    resultado = re.match(
        r"^(.+?)\s*\((\d+)\)$",
        descricao
    )

    if not resultado:
        return None

    return (
        resultado.group(1).strip(),
        resultado.group(2).strip()
    )


# ============================================================
# EXTRAIR LOTE E VALIDADE
# ============================================================

def extrair_lote_validade(texto):
    """
    Separa:

    Lote - Validade

    Exemplo:

    X3H841V - 30/09/2026
    """

    texto = texto.strip()

    if not texto:
        return "", ""

    if " - " not in texto:
        return texto, ""

    lote, validade = texto.rsplit(" - ", 1)

    return lote.strip(), validade.strip()


# ============================================================
# LOCALIZAR CABEÇALHO
# ============================================================

def obter_indices_cabecalho(linha):
    """
    Encontra a posição das colunas no cabeçalho.

    O G-MUS pode mudar a posição das células vazias
    entre diferentes páginas.
    """

    colunas_necessarias = [
        "Paciente",
        "Vacina, Estratégia e Dose",
        "Lote e Data de Validade",
        "Aplicado",
        "Qtde.",
        "Origem",
    ]

    for coluna in colunas_necessarias:

        if coluna not in linha:
            return None

    return {
        "paciente": linha.index("Paciente"),

        "vacina": linha.index(
            "Vacina, Estratégia e Dose"
        ),

        "lote": linha.index(
            "Lote e Data de Validade"
        ),

        "aplicado": linha.index(
            "Aplicado"
        ),

        "quantidade": linha.index(
            "Qtde."
        ),

        "origem": linha.index(
            "Origem"
        ),
    }


# ============================================================
# PROCESSAR ARQUIVO
# ============================================================

def processar_arquivo():

    registros = []

    problemas = []

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

            # Ainda não encontrou cabeçalho
            if indices is None:
                continue

            # ------------------------------------------------
            # Verifica se existem colunas suficientes
            # ------------------------------------------------

            maior_indice = max(
                indices.values()
            )

            if len(linha) <= maior_indice:
                continue

            # ------------------------------------------------
            # Extrai os campos mantendo células vazias
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
            # Ignora linhas vazias
            # ------------------------------------------------

            if not paciente:
                continue

            if paciente == "Paciente":
                continue

            if not descricao:
                continue

            # =================================================
            # CASO ESPECIAL:
            # DOSE ISOLADA
            #
            # Exemplo:
            # 3ª DOSE (3)
            #
            # Só será considerada dose isolada quando a linha
            # NÃO possuir " - ".
            # =================================================

            dose_isolada = extrair_dose_isolada(
                descricao
            )

            if dose_isolada is not None:

                nome_dose, codigo_dose = dose_isolada

                # Só associa à linha anterior se ela ainda
                # estiver sem dose.
                if registros:

                    ultimo = registros[-1]

                    if (
                        ultimo["Dose"] == ""
                        and ultimo["Código da dose"] == ""
                    ):

                        ultimo["Dose"] = nome_dose

                        ultimo[
                            "Código da dose"
                        ] = codigo_dose

                        ultimo[
                            "Vacina estratégia e dose"
                        ] = (
                            ultimo[
                                "Vacina estratégia e dose"
                            ].rstrip()
                            + " "
                            + nome_dose
                            + f" ({codigo_dose})"
                        )

                        continue

                # Se não encontrou registro anterior
                # compatível, registra para revisão.
                problemas.append(
                    (
                        numero_linha,
                        descricao
                    )
                )

                continue

            # =================================================
            # REGISTRO NORMAL DE VACINA
            # =================================================

            dados_vacina = extrair_vacina(
                descricao
            )

            if dados_vacina is None:

                problemas.append(
                    (
                        numero_linha,
                        descricao
                    )
                )

                continue

            # ------------------------------------------------
            # Lote e validade
            # ------------------------------------------------

            lote, validade = extrair_lote_validade(
                lote_validade
            )

            # ------------------------------------------------
            # Registro final
            # ------------------------------------------------

            registro = {
                "Nome do bairro":
                    NOME_BAIRRO,

                "Nome da vacina":
                    dados_vacina["Nome da vacina"],

                "Código da vacina":
                    dados_vacina["Código da vacina"],

                "Estratégia":
                    dados_vacina["Estratégia"],

                "Código da estratégia":
                    dados_vacina[
                        "Código da estratégia"
                    ],

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

    return registros, problemas


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
    print("LIMPEZA - VILA SÃO JOSÉ")
    print("=" * 60)

    # --------------------------------------------------------
    # Verifica arquivo de entrada
    # --------------------------------------------------------

    if not ARQUIVO_ENTRADA.exists():

        print()
        print(
            "ERRO: arquivo de entrada não encontrado."
        )

        print(
            f"Arquivo esperado: {ARQUIVO_ENTRADA}"
        )

        return

    # --------------------------------------------------------
    # Processa
    # --------------------------------------------------------

    registros, problemas = processar_arquivo()

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
        f"Registros não interpretados: {len(problemas)}"
    )

    print(
        f"Arquivo gerado: {ARQUIVO_SAIDA}"
    )

    # --------------------------------------------------------
    # Mostra problemas
    # --------------------------------------------------------

    if problemas:

        print()
        print(
            "REGISTROS QUE PRECISAM DE REVISÃO:"
        )

        for numero, descricao in problemas:

            print(
                f"Linha {numero}: {descricao}"
            )

    else:

        print()
        print(
            "Todos os registros foram "
            "interpretados com sucesso."
        )

    print()
    print(
        "Processamento concluído!"
    )


if __name__ == "__main__":
    main()