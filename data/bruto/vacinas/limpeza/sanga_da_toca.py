"""
Limpeza e padronização — Sanga da Toca
pyanalytics#17

Versão para VS Code / Python local.

Ordem de busca do CSV bruto:
1. Caminho padrão local.
2. Clone do repositório GitLab privado.
3. Se as duas tentativas falharem, solicita o caminho do CSV no terminal.

A lógica de limpeza é a mesma da versão Colab:
- mapeamento das colunas pelo cabeçalho de cada bloco do G-MUS;
- decomposição de "Vacina, Estratégia e Dose";
- separação de lote e validade;
- preservação de datas incompletas;
- manutenção de doses truncadas, sem inventar valores.

Não é definida uma quantidade esperada de registros, pois essa informação
não consta no arquivo-base enviado para Sanga da Toca.
"""

from pathlib import Path
import csv
import getpass
import re
import shutil
import subprocess

BASE_DIR = Path(".")
CAMINHO_PADRAO = (
    BASE_DIR / "data" / "bruto" / "vacinas"
    / "Sanga da Toca" / "Vacinas_Aplicadas_Sanga_da_Toca_Anonimizadas.csv"
)
CAMINHO_SAIDA = (
    BASE_DIR / "data" / "processed" / "vacinas"
    / "sanga_da_toca.csv"
)

NOME_BAIRRO = "Sanga da Toca"
REPO_URL = "https://codigos.ufsc.br/pyanalytics/pyanalytics.git"
CLONE_DIR = BASE_DIR / "pyanalytics_repo"
CAMINHO_RELATIVO_NO_REPO = CAMINHO_PADRAO.relative_to(BASE_DIR)

# Deixe vazio para solicitar o token de forma oculta.
GITLAB_TOKEN = ""

QUANTIDADE_ESPERADA = 936

COLUNAS_SAIDA = [
    "nome_do_bairro",
    "nome_da_vacina",
    "codigo_da_vacina",
    "estrategia",
    "codigo_da_estrategia",
    "dose",
    "codigo_da_dose",
    "vacina_estrategia_e_dose",
    "lote",
    "validade_do_lote",
    "data_da_aplicacao",
    "origem",
]

RE_DESCRICAO = re.compile(
    r"^(?P<vacina>.+?)\s*\((?P<cod_vacina>\d+)\)\s*-\s*"
    r"(?P<estrategia>.+?)\s*\((?P<cod_estrategia>\d+)\)\s*-\s*"
    r"(?P<dose>.+?)\s*\((?P<cod_dose>\d+)\)\s*$"
)

RE_DESCRICAO_SEM_DOSE = re.compile(
    r"^(?P<vacina>.+?)\s*\((?P<cod_vacina>\d+)\)\s*-\s*"
    r"(?P<estrategia>.+?)\s*\((?P<cod_estrategia>\d+)\)\s*-\s*$"
)

RE_DATA_COMPLETA = re.compile(r"^\d{2}/\d{2}/\d{4}$")
RE_DATA_MES_ANO = re.compile(r"^\d{2}/\d{4}$")


def tenta_obter_via_clone(nome_bairro: str):
    if shutil.which("git") is None:
        print("git não disponível neste ambiente; pulando clone.")
        return None

    caminho_no_clone = CLONE_DIR / CAMINHO_RELATIVO_NO_REPO

    if not CLONE_DIR.exists():
        token = GITLAB_TOKEN.strip()
        if not token:
            token = getpass.getpass(
                "Token GitLab (read_repository), oculto ao digitar: "
            ).strip()

        if not token:
            print("Nenhum token informado; pulando clone.")
            return None

        url_autenticada = REPO_URL.replace(
            "https://", f"https://oauth2:{token}@"
        )

        resultado = subprocess.run(
            ["git", "clone", "--depth", "1", url_autenticada, str(CLONE_DIR)],
            capture_output=True,
            text=True,
        )

        if resultado.returncode != 0:
            erro = resultado.stderr.strip().replace(token, "***")
            print("Falha ao clonar o repositório:")
            print(erro)
            return None

    if caminho_no_clone.exists():
        print(f"[{nome_bairro}] arquivo encontrado: {caminho_no_clone}")
        return caminho_no_clone

    print(f"[{nome_bairro}] arquivo não encontrado no clone.")
    return None


def obtem_caminho_arquivo():
    if CAMINHO_PADRAO.exists():
        print(f"Base encontrada em: {CAMINHO_PADRAO}")
        return CAMINHO_PADRAO

    print(f"Base não encontrada em: {CAMINHO_PADRAO}")

    caminho_via_clone = tenta_obter_via_clone(NOME_BAIRRO)
    if caminho_via_clone is not None:
        return caminho_via_clone

    caminho = input(
        f"Informe o caminho completo do CSV bruto de '{NOME_BAIRRO}': "
    ).strip().strip('"')

    if not caminho:
        raise FileNotFoundError("Nenhum caminho foi informado.")

    caminho = Path(caminho).expanduser()

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return caminho


def carrega_linhas(caminho: Path):
    with caminho.open(
        newline="", encoding="utf-8-sig", errors="replace"
    ) as arquivo:
        return list(csv.reader(arquivo))


def eh_linha_cabecalho_tabela(row):
    return (
        "Paciente" in row
        and any("Vacina, Estratégia e Dose" in c for c in row)
    )


def mapeia_colunas(header_row):
    idx = {}

    for i, valor in enumerate(header_row):
        valor = valor.strip()

        if valor == "Paciente":
            idx["paciente"] = i
        elif valor == "Vacina, Estratégia e Dose":
            idx["descricao"] = i
        elif valor == "Lote e Data de Validade":
            idx["lote_validade"] = i
        elif valor == "Aplicado":
            idx["aplicado"] = i
        elif valor == "Qtde.":
            idx["qtde"] = i
        elif valor == "Origem":
            idx["origem"] = i

    return idx


def get(row, idx_map, chave, default=""):
    i = idx_map.get(chave)

    if i is None or i >= len(row):
        return default

    return row[i].strip()


def limpa_base():
    caminho_entrada = obtem_caminho_arquivo()
    linhas = carrega_linhas(caminho_entrada)

    registros = []
    idx_map = None

    avisos_data_incompleta = 0
    avisos_dose_truncada = 0
    linhas_descartadas = 0

    for row in linhas:
        if not row or not any(c.strip() for c in row):
            continue

        if eh_linha_cabecalho_tabela(row):
            idx_map = mapeia_colunas(row)
            continue

        if idx_map is None:
            continue

        paciente = get(row, idx_map, "paciente")

        if paciente != "XXX":
            continue

        descricao = get(row, idx_map, "descricao")

        match = RE_DESCRICAO.match(descricao)
        dose = ""
        codigo_dose = ""

        if match:
            dose = match.group("dose").strip()
            codigo_dose = match.group("cod_dose")
        else:
            match = RE_DESCRICAO_SEM_DOSE.match(descricao)

            if match:
                avisos_dose_truncada += 1
            else:
                linhas_descartadas += 1
                continue

        lote_validade = get(row, idx_map, "lote_validade")

        if " - " in lote_validade:
            lote, validade = lote_validade.rsplit(" - ", 1)
        else:
            lote, validade = lote_validade, ""

        aplicado = get(row, idx_map, "aplicado")

        if not RE_DATA_COMPLETA.fullmatch(aplicado):
            avisos_data_incompleta += 1

        registros.append({
            "nome_do_bairro": NOME_BAIRRO,
            "nome_da_vacina": match.group("vacina").strip(),
            "codigo_da_vacina": match.group("cod_vacina"),
            "estrategia": match.group("estrategia").strip(),
            "codigo_da_estrategia": match.group("cod_estrategia"),
            "dose": dose,
            "codigo_da_dose": codigo_dose,
            "vacina_estrategia_e_dose": descricao.strip(),
            "lote": lote.strip(),
            "validade_do_lote": validade.strip(),
            "data_da_aplicacao": aplicado,
            "origem": get(row, idx_map, "origem"),
        })

    if not registros:
        raise ValueError("Nenhum registro de vacinação foi encontrado.")

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    with CAMINHO_SAIDA.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS_SAIDA,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(registros)

    validar(registros)

    print("\n===== RESULTADO =====")
    print(f"Entrada: {caminho_entrada}")
    print(f"Saída: {CAMINHO_SAIDA}")
    print(f"Registros processados: {len(registros)}")
    print(f"Datas completas: {sum(RE_DATA_COMPLETA.fullmatch(r['data_da_aplicacao']) is not None for r in registros)}")
    print(f"Datas MM/YYYY preservadas: {sum(RE_DATA_MES_ANO.fullmatch(r['data_da_aplicacao']) is not None for r in registros)}")
    print(f"Datas incompletas/fora do formato completo: {avisos_data_incompleta}")
    print(f"Doses truncadas na origem: {avisos_dose_truncada}")
    print(f"Linhas descartadas: {linhas_descartadas}")
    print("Validação: OK")


def validar(registros):
    if list(registros[0].keys()) != COLUNAS_SAIDA:
        raise AssertionError("Colunas fora do padrão.")

    if not all(r["nome_do_bairro"] == NOME_BAIRRO for r in registros):
        raise AssertionError("Há registros com bairro diferente do esperado.")

    if not all(r["codigo_da_vacina"].isdigit() for r in registros):
        raise AssertionError("Há código de vacina não numérico.")

    if len(registros) != QUANTIDADE_ESPERADA:
        raise AssertionError(f"Quantidade inesperada de registros: {len(registros)}. Esperado: {QUANTIDADE_ESPERADA}.")

    # Não exige uma origem específica: o arquivo enviado não informa
    # uma regra de validação desse tipo para Sanga da Toca.


if __name__ == "__main__":
    limpa_base()
