"""
Limpeza e padronização da base de vacinas aplicadas.
Sala de Vacinação / Bairro: POLÍCIA RODOVIÁRIA — pyanalytics#17

Versão para VS Code / Python local.

O script busca o CSV bruto em três etapas, na ordem:
    1. Caminho padrão local (CAMINHO_PADRAO, abaixo).
    2. Clone do repositório GitLab privado (REPO_URL) — usa o token em
       GITLAB_TOKEN (abaixo, na seção de configurações) se estiver
       preenchido; caso contrário, pede o token na hora (oculto).
    3. Se as duas etapas acima falharem, solicita o caminho do CSV no
       terminal.

O CSV padronizado é gravado em data/processed/vacinas/policia_rodoviaria.csv

Regras de limpeza:
- O relatório bruto (export do sistema G-MUS) intercala cabeçalhos de
  página, linhas de filtro, linhas "Vacina: <nome> (<código>)" e
  rodapés com os registros de aplicação. O layout de colunas varia
  ligeiramente entre blocos, por isso a leitura mapeia as colunas pelo
  cabeçalho de cada bloco (",Paciente,...") em vez de usar índice fixo.
- "Vacina, Estratégia e Dose" é decomposta em nome/código da vacina,
  estratégia/código e dose/código.
- "Lote e Data de Validade" é separada em lote e validade.
- Registros com dose truncada na origem (quebra de página) são
  mantidos com dose/código em branco, sem inventar o valor.
- Datas de aplicação que vêm apenas como MM/AAAA (sem dia) na fonte
  são mantidas como estão, sem inventar o dia.
"""

from __future__ import annotations

import csv
import getpass
import re
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(".")

# Ajuste aqui se o arquivo bruto estiver em outro lugar
CAMINHO_PADRAO = BASE_DIR / "data" / "bruto" / "vacinas" / "Policia Rodoviaria" / "Vacinas_Aplicadas_Policia_Rodoviaria_Anonimizadas.csv"
CAMINHO_SAIDA = BASE_DIR / "data" / "processed" / "vacinas" / "policia_rodoviaria.csv"
NOME_BAIRRO = "Polícia Rodoviária"

# Repositório privado que contém os caminhos de dados do projeto.
REPO_URL = "https://codigos.ufsc.br/pyanalytics/pyanalytics.git"
CLONE_DIR = BASE_DIR / "pyanalytics_repo"
CAMINHO_RELATIVO_NO_REPO = CAMINHO_PADRAO.relative_to(BASE_DIR)

# Token de acesso do GitLab (Settings > Access Tokens, escopo
# read_repository), usado para clonar o repositório privado acima.
#
#   COLE O TOKEN AQUI, entre as aspas, se quiser deixá-lo fixo no
#   script:
GITLAB_TOKEN = ""
#
# Atenção: colar o token aqui é conveniente, mas ele fica salvo em
# texto puro neste arquivo — não faça commit/compartilhe o arquivo
# com o token preenchido. Se GITLAB_TOKEN ficar em branco (""), o
# script pede o token na hora, de forma oculta (getpass), sem
# deixá-lo salvo em lugar nenhum.

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

# "Vacina raiva em cultivo celular vero (37) - Pós-exposição (13) - 4ª DOSE (4)"
RE_DESCRICAO = re.compile(
    r"^(?P<vacina>.+?)\s*\((?P<cod_vacina>\d+)\)\s*-\s*"
    r"(?P<estrategia>.+?)\s*\((?P<cod_estrategia>\d+)\)\s*-\s*"
    r"(?P<dose>.+?)\s*\((?P<cod_dose>\d+)\)\s*$"
)

# Fallback para registros com a parte da dose truncada no arquivo de
# origem (ex.: "... - Rotina (1) - ", cortado numa quebra de página).
RE_DESCRICAO_SEM_DOSE = re.compile(
    r"^(?P<vacina>.+?)\s*\((?P<cod_vacina>\d+)\)\s*-\s*"
    r"(?P<estrategia>.+?)\s*\((?P<cod_estrategia>\d+)\)\s*-\s*$"
)

# Formato completo dd/mm/aaaa
RE_DATA_COMPLETA = re.compile(r"^\d{2}/\d{2}/\d{4}$")


# --------------------------------------------------------------------
# Clone do repositório GitLab (2ª tentativa, antes do upload manual)
# --------------------------------------------------------------------
def tenta_obter_via_clone(nome_bairro: str) -> Path | None:
    """Tenta obter o CSV bruto clonando o repositório GitLab privado.

    Retorna o caminho do arquivo dentro do clone, ou None se o clone
    não for possível (git ausente, sem token, falha de autenticação,
    repositório sem o arquivo esperado etc.) — nesse caso o chamador
    segue para o fallback de upload/caminho manual.
    """
    if shutil.which("git") is None:
        print("git não disponível neste ambiente; pulando clone do repositório.")
        return None

    caminho_no_clone = CLONE_DIR / CAMINHO_RELATIVO_NO_REPO

    if CLONE_DIR.exists():
        print(f"Repositório já clonado em: {CLONE_DIR}")
    else:
        print(f"Base não encontrada localmente. Clonando {REPO_URL} ...")

        token = GITLAB_TOKEN.strip()
        if token:
            print("Usando o token preenchido em GITLAB_TOKEN.")
        else:
            token = getpass.getpass(
                "Token de acesso do GitLab (Personal/Project Access Token, "
                "escopo read_repository) — não fica visível ao digitar: "
            ).strip()

        if not token:
            print("Nenhum token informado; pulando clone do repositório.")
            return None

        url_autenticada = REPO_URL.replace("https://", f"https://oauth2:{token}@")
        resultado = subprocess.run(
            ["git", "clone", "--depth", "1", url_autenticada, str(CLONE_DIR)],
            capture_output=True, text=True,
        )
        if resultado.returncode != 0:
            # remove o token de qualquer mensagem de erro antes de exibir
            erro = resultado.stderr.strip().replace(token, "***")
            print("Falha ao clonar o repositório:")
            print(erro)
            return None
        print(f"Repositório clonado em: {CLONE_DIR}")

    if caminho_no_clone.exists():
        print(f"[{nome_bairro}] arquivo encontrado no repositório clonado: {caminho_no_clone}")
        return caminho_no_clone

    print(f"[{nome_bairro}] arquivo não encontrado em {caminho_no_clone} dentro do repositório clonado.")
    return None


# --------------------------------------------------------------------
# Fallback de upload / seleção manual do arquivo bruto
# --------------------------------------------------------------------
def obtem_caminho_arquivo(caminho_padrao: Path, nome_bairro: str) -> Path:
    """Garante um caminho válido para o CSV bruto, tentando nesta ordem:
    1) caminho padrão local; 2) clone do repositório GitLab; 3) caminho
    informado no terminal.
    """
    if caminho_padrao.exists():
        print(f"Base encontrada em: {caminho_padrao}")
        return caminho_padrao

    print(f"Base não encontrada em: {caminho_padrao}")

    caminho_via_clone = tenta_obter_via_clone(nome_bairro)
    if caminho_via_clone is not None:
        return caminho_via_clone

    caminho_informado = input(f"Informe o caminho completo do CSV bruto de '{nome_bairro}': ").strip()
    caminho_informado = Path(caminho_informado)
    if not caminho_informado.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_informado}")
    return caminho_informado


# --------------------------------------------------------------------
# Parsing do relatório bruto
# --------------------------------------------------------------------
def carrega_linhas(caminho: Path):
    with caminho.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def eh_linha_cabecalho_tabela(row):
    """Identifica a linha ' ,Paciente,,,"Vacina, Estratégia e Dose",...' """
    return "Paciente" in row and any("Vacina, Estratégia e Dose" in c for c in row)


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
    caminho_entrada = obtem_caminho_arquivo(CAMINHO_PADRAO, NOME_BAIRRO)
    linhas = carrega_linhas(caminho_entrada)

    registros = []
    idx_map = None
    avisos_data_incompleta = 0
    avisos_dose_truncada = 0
    linhas_descartadas = 0

    for row in linhas:
        if not row or not any(c.strip() for c in row):
            continue

        # Nova tabela de colunas (início de bloco / nova página)
        if eh_linha_cabecalho_tabela(row):
            idx_map = mapeia_colunas(row)
            continue

        # Linhas de cabeçalho de página, filtro, totais e rodapé: ignorar
        if idx_map is None:
            continue

        paciente = get(row, idx_map, "paciente")
        if paciente != "XXX":
            # linhas de "Quantidade:", "Total por Vacina:", rodapé etc.
            continue

        descricao = get(row, idx_map, "descricao")
        m = RE_DESCRICAO.match(descricao)
        dose, cod_dose = "", ""
        if m:
            dose, cod_dose = m.group("dose").strip(), m.group("cod_dose")
        else:
            m_sem_dose = RE_DESCRICAO_SEM_DOSE.match(descricao)
            if m_sem_dose:
                # Dose truncada na origem: mantém o registro, dose em branco
                m = m_sem_dose
                avisos_dose_truncada += 1
            else:
                # descrição vazia/fora do padrão (linha sem dado real): descartada
                linhas_descartadas += 1
                continue

        lote_validade = get(row, idx_map, "lote_validade")
        if " - " in lote_validade:
            lote, validade = lote_validade.rsplit(" - ", 1)
        else:
            lote, validade = lote_validade, ""

        aplicado = get(row, idx_map, "aplicado")
        if not RE_DATA_COMPLETA.match(aplicado):
            # No arquivo bruto, alguns blocos trazem apenas mes/ano
            # (ex.: "02/2026") em vez da data completa. Mantido como
            # veio da origem para nao inventar o dia; contabilizado
            # para conferência.
            avisos_data_incompleta += 1

        origem = get(row, idx_map, "origem")

        registros.append({
            "nome_do_bairro": NOME_BAIRRO,
            "nome_da_vacina": m.group("vacina").strip(),
            "codigo_da_vacina": m.group("cod_vacina"),
            "estrategia": m.group("estrategia").strip(),
            "codigo_da_estrategia": m.group("cod_estrategia"),
            "dose": dose,
            "codigo_da_dose": cod_dose,
            "vacina_estrategia_e_dose": descricao.strip(),
            "lote": lote.strip(),
            "validade_do_lote": validade.strip(),
            "data_da_aplicacao": aplicado,
            "origem": origem,
        })

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS_SAIDA)
        writer.writeheader()
        writer.writerows(registros)

    print(f"Registros processados: {len(registros)}")
    print(f"Registros com data de aplicação incompleta (mes/ano apenas): {avisos_data_incompleta}")
    print(f"Registros com dose truncada na origem (mantidos, dose em branco): {avisos_dose_truncada}")
    print(f"Linhas descartadas (sem dado real de vacina): {linhas_descartadas}")
    print(f"Arquivo salvo em: {CAMINHO_SAIDA}")

    return registros


def validar(registros):
    """Valida a base antes de considerá-la pronta para entrega."""
    if not registros:
        raise ValueError("Nenhum registro de vacinação foi encontrado.")

    if list(registros[0].keys()) != COLUNAS_SAIDA:
        raise AssertionError("Colunas fora do padrão.")

    if len(registros) != 3290:
        raise AssertionError(
            f"Quantidade inesperada de registros: {len(registros)}. "
            "Esperado: 3290. Confira o CSV bruto antes de entregar."
        )

    if not all(r["nome_do_bairro"] == NOME_BAIRRO for r in registros):
        raise AssertionError("Há registros com bairro diferente do esperado.")

    if not all(r["origem"] in ("Carteirinha", "Prontuário", "Tela de Aplicação") for r in registros):
        raise AssertionError("Há registros com origem fora do padrão (Carteirinha/Prontuário/Tela de Aplicação).")

    if not all(r["codigo_da_vacina"].isdigit() for r in registros):
        raise AssertionError("Há registros com código de vacina não numérico.")

    resumo = {
        "registros": len(registros),
        "datas_completas": sum(
            bool(RE_DATA_COMPLETA.fullmatch(r["data_da_aplicacao"]))
            for r in registros
        ),
        "datas_mes_ano_preservadas": sum(
            bool(re.fullmatch(r"\d{2}/\d{4}", r["data_da_aplicacao"]))
            for r in registros
        ),
        "estrategias_ausentes": sum(
            not r["codigo_da_estrategia"] for r in registros
        ),
        "doses_ausentes": sum(
            not r["codigo_da_dose"] for r in registros
        ),
    }
    return resumo


def main():
    registros = limpa_base()
    resumo = validar(registros)

    print("\n===== VALIDAÇÃO =====")
    print(f"Registros: {resumo['registros']}")
    print(f"Datas completas: {resumo['datas_completas']}")
    print(f"Datas MM/YYYY preservadas: {resumo['datas_mes_ano_preservadas']}")
    print(f"Estratégias sem código: {resumo['estrategias_ausentes']}")
    print(f"Doses sem código: {resumo['doses_ausentes']}")
    print("Validação: OK")


if __name__ == "__main__":
    main()
