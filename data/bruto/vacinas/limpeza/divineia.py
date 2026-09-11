import os               # manipula pastas, caminhos e arquivos do sistema
import re               # faz limpeza e busca de padroes em textos
import glob             # procura arquivos no computador usando partes do nome
import pandas as pd     # trata tabelas e dados

# Pastas e caminhos
PASTA_PROCESSADOS = os.path.join("data", "processed", "vacinas")
CAMINHO_SAIDA = os.path.join(PASTA_PROCESSADOS, "divineia.csv")

def achar_arquivo_bruto():
    caminho = os.path.join(
        "data", "bruto", "vacinas", "Divineia", "Vacinas_Aplicadas_Divineia_Anonimizadas.csv"
    )
    if os.path.exists(caminho):
        return caminho
    busca = glob.glob("data/bruto/vacinas/*Divin*/*.csv")
    return busca[0] if busca else caminho

# Padroniza para DD/MM/AAAA
def arrumar_data(data):
    if pd.isna(data):
        return ""
    txt = str(data).strip()
    if txt == "" or txt.lower() in ["nan", "none", "nat"]:
        return ""
    data_certa = pd.to_datetime(txt, errors="coerce", dayfirst=True)
    return "" if pd.isna(data_certa) else data_certa.strftime("%d/%m/%Y")

# Separa vacina, estrategia e dose pelo traco
def separar_vacina(texto):
    if not isinstance(texto, str):
        return "", "", ""
    partes = [re.sub(r"\s+", " ", p).strip() for p in texto.split("-")]
    vacina = partes[0] if len(partes) > 0 else ""
    estrategia = partes[1] if len(partes) > 1 else ""
    dose = partes[2] if len(partes) > 2 else ""
    return vacina, estrategia, dose

# Mapeia codigos oficiais
def codigo_vacina(nome):
    n = str(nome).upper()
    if "INFLUENZA" in n:
        return 33
    elif "COVID" in n:
        return 85
    elif "FEBRE AMARELA" in n:
        return 11
    elif "HEPATITE" in n:
        return 23
    elif "TRIPLICE" in n or "TRÍPLICE" in n:
        return 21
    elif "POLIO" in n or "POLIOMIELITE" in n:
        return 25
    elif "ROTAVIRUS" in n or "ROTAVÍRUS" in n:
        return 40
    return None

def codigo_estrategia(est):
    e = str(est).upper()
    if "ROTINA" in e:
        return 1
    elif "ESPECIAL" in e:
        return 2
    elif "POS" in e or "PÓS" in e:
        return 3
    elif "BLOQUEIO" in e:
        return 4
    elif "CAMPANHA" in e:
        return 5
    return None

def codigo_dose(dose):
    d = str(dose).upper()
    if "1" in d and "REFOR" not in d:
        return 1
    elif "2" in d and "REFOR" not in d:
        return 2
    elif "3" in d and "REFOR" not in d:
        return 3
    elif "UNICA" in d or "ÚNICA" in d:
        return 8
    elif "REFOR" in d:
        return 9
    return None

def limpar_lote(lote):
    if pd.isna(lote):
        return ""
    txt = str(lote).strip()
    if "/" in txt:
        txt = txt.split("/")[0].strip()
    txt = re.sub(r'["\']', '', txt)
    return "" if txt.lower() in ["nan", "none", "sem lote", "indefinido"] else txt

# Separa lote e validade se vierem na mesma coluna
def tratar_lote_validade(df):
    col_lote = next((c for c in df.columns if c.lower() == "lote"), None)
    col_val = next((c for c in df.columns if "validade" in c.lower()), None)
    
    if col_lote and col_val:
        return df[col_lote].apply(limpar_lote), df[col_val].apply(arrumar_data)

    col_combo = next((c for c in df.columns if "lote" in c.lower()), None)
    if col_combo:
        texto = df[col_combo].astype(str)
        lote = texto.apply(limpar_lote)
        validade = texto.apply(lambda x: arrumar_data(x.split("/")[1].strip()) if "/" in str(x) else "")
        return lote, validade

    return "", ""

# Le csv com delimitador flexivel
def ler_csv(caminho):
    for sep in [";", ","]:
        for enc in ["latin1", "utf-8"]:
            try:
                dados = pd.read_csv(caminho, sep=sep, encoding=enc)
                if dados.shape[1] > 1:
                    dados.columns = dados.columns.astype(str).str.strip()
                    return dados
            except Exception:
                continue
    return pd.read_csv(caminho, sep=None, engine="python", encoding="latin1")

def executar():
    caminho_bruto = achar_arquivo_bruto()
    print(f"Processando: {caminho_bruto}")

    # 1. Carrega dados
    df_bruto = ler_csv(caminho_bruto).dropna(how="all")

    # 2. Cria base padronizada
    df_limpo = pd.DataFrame()
    df_limpo["Nome do bairro"] = "Divineia"

    # 3. Trata vacina, estrategia e dose
    col_ved = next((c for c in df_bruto.columns if "vacina" in c.lower()), df_bruto.columns[0])
    df_limpo["Vacina estratégia e dose"] = df_bruto[col_ved].astype(str).str.strip()

    partes = df_limpo["Vacina estratégia e dose"].apply(separar_vacina)
    df_limpo["Nome da vacina"] = [p[0] for p in partes]
    df_limpo["Estratégia"] = [p[1] for p in partes]
    df_limpo["Dose"] = [p[2] for p in partes]

    # 4. Gera codigos numericos
    df_limpo["Código da vacina"] = df_limpo["Nome da vacina"].apply(codigo_vacina).astype("Int64")
    df_limpo["Código da estratégia"] = df_limpo["Estratégia"].apply(codigo_estrategia).astype("Int64")
    df_limpo["Código da dose"] = df_limpo["Dose"].apply(codigo_dose).astype("Int64")

    # 5. Lote e validade
    lote, validade = tratar_lote_validade(df_bruto)
    df_limpo["Lote"] = lote
    df_limpo["Validade do lote"] = validade

    # 6. Data da aplicacao
    col_data = next((c for c in df_bruto.columns if "aplica" in c.lower() or "data" in c.lower()), None)
    df_limpo["Data da aplicação"] = df_bruto[col_data].apply(arrumar_data) if col_data else ""

    # 7. Origem
    col_origem = next((c for c in df_bruto.columns if "origem" in c.lower()), None)
    df_limpo["Origem"] = df_bruto[col_origem].astype(str).str.strip() if col_origem else "Prontuário"
    df_limpo["Origem"] = df_limpo["Origem"].replace(["nan", "None", ""], "Prontuário")

    # 8. Ordena colunas conforme regra da sprint
    colunas_finais = [
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
    df_limpo = df_limpo[colunas_finais]

    # Remove vazios e duplicados
    df_limpo = df_limpo[df_limpo["Nome da vacina"] != ""].drop_duplicates()

    # 9. Salva resultado
    os.makedirs(PASTA_PROCESSADOS, exist_ok=True)
    df_limpo.to_csv(CAMINHO_SAIDA, index=False, encoding="utf-8")
    print(f"Salvo com sucesso: {CAMINHO_SAIDA}")

if __name__ == "__main__":
    executar()