from pathlib import Path
import csv
import re
import pandas as pd

# Estrutura esperada:
# /data/bruto/vacinas/ -> CSV bruto do bairro
# /data/bruto/vacinas/Limpeza/ -> este script
# /data/processed/vacinas/ -> CSV padronizado
#
# O script não inventa informações ausentes.
# Datas no formato MM/YYYY permanecem MM/YYYY quando o dia não existe no bruto.
# Da mesma forma, uma estratégia/dose ausente no bruto permanece vazia.

SCRIPT_DIR = Path(__file__).resolve().parent
BAIRRO_DIR = SCRIPT_DIR.parent
PASTA_BRUTA = BAIRRO_DIR
ARQUIVO_SAIDA = BAIRRO_DIR.parents[2] / "processed" / "vacinas" / "sanga_da_areia.csv"
BAIRRO = "Sanga da Areia"

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


def encontrar_arquivo_bruto():
    candidatos = [
        PASTA_BRUTA / "Vacinas_Aplicadas_Sanga_da_Areia_Anonimizadas.csv",
        PASTA_BRUTA / "sanga_da_areia.csv",
    ]
    for caminho in candidatos:
        if caminho.exists():
            return caminho

    encontrados = [
        p for p in PASTA_BRUTA.glob("*.csv")
        if "sanga" in p.name.lower() and "areia" in p.name.lower()
    ]
    if len(encontrados) == 1:
        return encontrados[0]
    if not encontrados:
        raise FileNotFoundError(
            f"Nenhum CSV da Sanga da Areia encontrado em {PASTA_BRUTA}"
        )
    raise RuntimeError(
        "Mais de um CSV da Sanga da Areia foi encontrado; "
        "deixe apenas o arquivo bruto correto ou ajuste a lista de candidatos."
    )


def limpar_texto(valor):
    return str(valor).replace("\xa0", " ").strip()


def extrair_campos_descricao(descricao):
    descricao = limpar_texto(descricao)
    partes = [p.strip() for p in descricao.split(" - ")]

    vac_part = partes[0] if len(partes) >= 1 else ""
    estrategia_part = partes[1] if len(partes) >= 2 else ""
    dose_part = partes[2] if len(partes) >= 3 else ""

    m = re.match(r"^(.*?)\s*\((\d+)\)$", vac_part)
    if m:
        nome_vacina, codigo_vacina = m.group(1).strip(), m.group(2)
    else:
        nome_vacina, codigo_vacina = vac_part, ""

    m = re.match(r"^(.*?)\s*\((\d+)\)$", estrategia_part)
    if m:
        estrategia, codigo_estrategia = m.group(1).strip(), m.group(2)
    else:
        estrategia = estrategia_part.rstrip(" -").strip()
        codigo_estrategia = ""

    m = re.match(r"^(.*?)\s*\((\d+)\)$", dose_part)
    if m:
        dose, codigo_dose = m.group(1).strip(), m.group(2)
    else:
        dose, codigo_dose = dose_part, ""

    return (
        nome_vacina,
        codigo_vacina,
        estrategia,
        codigo_estrategia,
        dose,
        codigo_dose,
    )


def extrair_lote_validade(valor):
    valor = limpar_texto(valor)
    if " - " in valor:
        lote, validade = valor.split(" - ", 1)
        return lote.strip(), validade.strip()
    return valor, ""


def ler_linhas_brutas(caminho):
    with caminho.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        return list(csv.reader(f))


def padronizar(caminho):
    linhas = ler_linhas_brutas(caminho)
    registros = []

    for numero_linha, row in enumerate(linhas, start=1):
        if len(row) < 11:
            continue

        paciente = limpar_texto(row[1])
        descricao = limpar_texto(row[4])

        if paciente != "XXX" or not descricao.startswith("Vacina "):
            continue

        lote_validade = limpar_texto(row[7])
        tail = [limpar_texto(x) for x in row[8:] if limpar_texto(x)]

        if len(tail) < 3:
            raise ValueError(
                f"Linha {numero_linha}: não foi possível localizar "
                "data de aplicação, quantidade e origem."
            )

        data_aplicacao, quantidade, origem = tail[-3], tail[-2], tail[-1]

        (
            nome_vacina,
            codigo_vacina,
            estrategia,
            codigo_estrategia,
            dose,
            codigo_dose,
        ) = extrair_campos_descricao(descricao)

        lote, validade = extrair_lote_validade(lote_validade)

        registros.append({
            "Nome do bairro": BAIRRO,
            "Nome da vacina": nome_vacina,
            "Código da vacina": codigo_vacina,
            "Estratégia": estrategia,
            "Código da estratégia": codigo_estrategia,
            "Dose": dose,
            "Código da dose": codigo_dose,
            "Vacina estratégia e dose": descricao,
            "Lote": lote,
            "Validade do lote": validade,
            "Data da aplicação": data_aplicacao,
            "Origem": origem,
        })

    return pd.DataFrame(registros, columns=COLUNAS_SAIDA)


def validar(df):
    assert list(df.columns) == COLUNAS_SAIDA, "Colunas fora do padrão."
    assert len(df) == 1405, (
        f"Quantidade inesperada de registros: {len(df)}. "
        "Confira o bruto antes de entregar."
    )
    assert df["Nome do bairro"].eq(BAIRRO).all()
    assert df["Origem"].isin(["Carteirinha", "Prontuário", "Tela de Aplicação"]).all()
    assert pd.to_numeric(df["Código da vacina"], errors="coerce").notna().all()

    return {
        "registros": len(df),
        "datas_completas": int(df["Data da aplicação"].str.fullmatch(r"\d{2}/\d{2}/\d{4}", na=False).sum()),
        "datas_mes_ano_preservadas": int(df["Data da aplicação"].str.fullmatch(r"\d{2}/\d{4}", na=False).sum()),
        "estrategias_ausentes": int(df["Código da estratégia"].eq("").sum()),
        "doses_ausentes": int(df["Código da dose"].eq("").sum()),
    }


def main():
    entrada = encontrar_arquivo_bruto()
    df = padronizar(entrada)
    resumo = validar(df)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )

    print(f"Entrada: {entrada}")
    print(f"Saída:   {ARQUIVO_SAIDA}")
    print(f"Registros: {resumo['registros']}")
    print(f"Datas completas: {resumo['datas_completas']}")
    print(f"Datas MM/YYYY preservadas: {resumo['datas_mes_ano_preservadas']}")
    print(f"Estratégias sem código no bruto: {resumo['estrategias_ausentes']}")
    print(f"Doses sem código no bruto: {resumo['doses_ausentes']}")


if __name__ == "__main__":
    main()
