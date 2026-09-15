import os
import re
import csv
import pandas as pd

BAIRRO_NOME = "Mato Alto Lagoão"

PASTA_BRUTO = os.path.join(
    "data",
    "bruto",
    "vacinas",
    "Mato Alto Lagoao"
)

ARQUIVO_BRUTO = os.path.join(
    PASTA_BRUTO,
    "Vacinas_Aplicadas_Mato_Alto_Lagoao_Anonimizadas.csv"
)

PASTA_PROCESSADOS = os.path.join(
    "data",
    "processed",
    "vacinas"
)

CAMINHO_SAIDA = os.path.join(
    PASTA_PROCESSADOS,
    "mato_alto_lagao.csv"
)

#Remove espaços extras e caracteres invisíveis
def limpar_texto(valor):
    if valor is None:
        return ""

    return str(valor).replace("\xa0", " ").strip()

#Padroniza a data de validade para o formato DD/MM/AAAA.
def arrumar_validade(data):
    data = limpar_texto(data)

    if not data:
        return ""

    if data.lower() in {"nan", "none", "nat", "0", "00/00/0000"}:
        return ""

    resultado = pd.to_datetime(
        data,
        errors="coerce",
        dayfirst=True
    )

    if pd.isna(resultado):
        return ""

    return resultado.strftime("%d/%m/%Y")

# Padroniza a data da aplicação para aceitar formatos completos ou parciais (mês/ano)
def arrumar_aplicado(data):
    data = limpar_texto(data)

    if not data:
        return ""

    if re.fullmatch(r"\d{2}/\d{4}", data):
        return data

    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", data):
        resultado = pd.to_datetime(
            data,
            errors="coerce",
            dayfirst=True
        )

        if pd.isna(resultado):
            return ""

        return resultado.strftime("%d/%m/%Y")

    return data

#Separa a string que contém o lote e a data de validade unidos por hífen
def extrair_lote_validade(valor):
    valor = limpar_texto(valor)

    if not valor:
        return "", ""

    match = re.match(
        r"^(.*?)\s*-\s*(\d{2}/\d{2}/\d{4})\s*$",
        valor
    )

    if match:
        lote = match.group(1).strip()
        validade = arrumar_validade(match.group(2))
        return lote, validade

    return valor, ""

#Extrai nomes e códigos de vacina, estratégia e dose usando Regex
def extrair_vacina_estrategia_dose(texto):
    texto = limpar_texto(texto)

    if not texto:
        return "", "", "", "", "", ""

    padrao = re.compile(
        r"^(.*?)\s*\((\d+)\)"
        r"\s*-\s*(.*?)\s*\((\d+)\)"
        r"\s*-\s*(.*?)\s*\((\d+)\)\s*$"
    )

    match = padrao.match(texto)

    if not match:
        return texto, "", "", "", "", ""

    return (
        match.group(1).strip(),
        match.group(2).strip(),
        match.group(3).strip(),
        match.group(4).strip(),
        match.group(5).strip(),
        match.group(6).strip()
    )

def processar_dados():

    print("Lendo arquivo bruto:")
    print(ARQUIVO_BRUTO)

    if not os.path.exists(ARQUIVO_BRUTO):
        raise FileNotFoundError(
            f"Arquivo não encontrado:\n{ARQUIVO_BRUTO}"
        )

    registros = []

    vacina_atual = ""

    linhas_ignoradas = 0

    with open(
        ARQUIVO_BRUTO,
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline=""
    ) as arquivo:

        leitor = csv.reader(arquivo)

        for linha_numero, linha in enumerate(leitor, start=1):

            linha = [limpar_texto(x) for x in linha]

            while linha and linha[-1] == "":
                linha.pop()

            if not linha:
                linhas_ignoradas += 1
                continue

            primeira = linha[0] if len(linha) > 0 else ""

#Ignora linhas de cabeçalho por grupo de vacina
            if primeira.lower().startswith("vacina:"):
                vacina_atual = primeira.split(":", 1)[1].strip()
                continue

            texto_linha = " | ".join(linha)

            if "Paciente" in texto_linha and \
               "Vacina, Estratégia e Dose" in texto_linha:
                continue

            if "Relatório emitido pelo sistema G-MUS" in texto_linha:
                continue

            if "© Inovadora Sistemas de Gestão Ltda." in texto_linha:
                continue

            if re.search(r"Página:\s*\d+", texto_linha):
                continue

            if primeira in {
                "Vacinas Aplicadas",
                "Filtros:"
            }:
                continue

            if "Quantidade:" in texto_linha:
                continue

            if "Total por Vacina:" in texto_linha:
                continue

            if len(linha) < 5:
                linhas_ignoradas += 1
                continue

            paciente = linha[1] if len(linha) > 1 else ""

            if not paciente:
                continue

            indice_descricao = None

            for i, valor in enumerate(linha):
                if re.search(
                    r"\s-\s.*?\(\d+\)\s-\s",
                    valor
                ):
                    indice_descricao = i
                    break

            if indice_descricao is None:
                linhas_ignoradas += 1
                continue

            descricao = linha[indice_descricao]

# Identifica o índice do lote e faz a extração do lote + validade
            indice_lote = None

            for i in range(
                indice_descricao + 1,
                len(linha)
            ):
                valor = linha[i]

                if re.search(
                    r"\d{2}/\d{2}/\d{4}\s*$",
                    valor
                ):
                    indice_lote = i
                    break

            if indice_lote is not None:
                lote, validade = extrair_lote_validade(
                    linha[indice_lote]
                )
            else:
                lote = ""
                validade = ""

            origem = ""

# Identifica a origem da aplicação (ex: Carteirinha, Transcrição, Campanha)

            for valor in reversed(linha):
                if valor in {
                    "Carteirinha",
                    "Transcrição",
                    "Campanha",
                    "Demanda",
                    "Rede privada"
                }:
                    origem = valor
                    break

            aplicado = ""

            for i, valor in enumerate(linha):

                if i == indice_lote:
                    continue

                if re.fullmatch(
                    r"\d{2}/\d{4}",
                    valor
                ):
                    aplicado = arrumar_aplicado(valor)
                    break

                if re.fullmatch(
                    r"\d{2}/\d{2}/\d{4}",
                    valor
                ):
                    aplicado = arrumar_aplicado(valor)
                    break

            (
                nome_vacina,
                codigo_vacina,
                estrategia,
                codigo_estrategia,
                dose,
                codigo_dose
            ) = extrair_vacina_estrategia_dose(
                descricao
            )

            registros.append({
                "Nome do bairro": BAIRRO_NOME,
                "Nome da vacina": nome_vacina,
                "Código da vacina": codigo_vacina,
                "Estratégia": estrategia,
                "Código da estratégia": codigo_estrategia,
                "Dose": dose,
                "Código da dose": codigo_dose,
                "Vacina estratégia e dose": descricao,
                "Lote": lote,
                "Validade do lote": validade,
                "Data da aplicação": aplicado,
                "Origem": origem
            })

    df_final = pd.DataFrame(registros)

    df_final = df_final[
        df_final["Vacina estratégia e dose"]
        .astype(str)
        .str.strip() != ""
    ]

    os.makedirs(
        PASTA_PROCESSADOS,
        exist_ok=True
    )

    df_final.to_csv(
        CAMINHO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

if __name__ == "__main__":
    processar_dados()