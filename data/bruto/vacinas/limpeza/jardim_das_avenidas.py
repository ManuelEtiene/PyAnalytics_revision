import os     # manipula pastas, caminhos e arquivos do sistema
import re     # faz limpeza e busca de padroes em textos
import glob   # procura arquivos no computador usando partes do nome
import pandas as pd  # trata tabelas e dados, similar ao excel

# Pastas e caminhos
PASTA_PROCESSADOS = os.path.join("data", "processed", "vacinas")
CAMINHO_SAIDA = os.path.join(PASTA_PROCESSADOS, "jardim_das_avenidas.csv")

def achar_arquivo_bruto():
    caminho = os.path.join(
        "data", "bruto", "vacinas", "Jardim das Avenidas", "Vacinas_Aplicadas_Jardim_das_Avenidas_Anonimizadas.csv"
    )
    if os.path.exists(caminho):
        return caminho
    busca = glob.glob("data/bruto/vacinas/*Jardim*/*.csv")
    return busca[0] if busca else caminho

def arrumar_data(data):
    if pd.isna(data):
        return ""
    txt = str(data).strip()
    if txt == "" or txt.lower() in ["nan", "none", "nat"]:
        return ""
    data_certa = pd.to_datetime(txt, errors="coerce", dayfirst=True)
    return "" if pd.isna(data_certa) else data_certa.strftime("%d/%m/%Y")

def separar_vacina(texto):
    if not isinstance(texto, str) or texto.strip() == "":
        return "", "", ""
    partes = [re.sub(r"\s+", " ", p).strip() for p in texto.split("-")]
    vacina = partes[0] if len(partes) > 0 else ""
    estrategia = partes[1] if len(partes) > 1 else ""
    dose = partes[2] if len(partes) > 2 else ""
    return vacina, estrategia, dose

def codigo_vacina(nome):
    n = str(nome).upper()
    if "INFLUENZA" in n or "GRIPE" in n:
        return 33
    elif "COVID" in n:
        return 85
    elif "FEBRE AMARELA" in n:
        return 11
    elif "HEPATITE B" in n:
        return 23
    elif "HEPATITE A" in n:
        return 24
    elif "TRIPLICE BACTERIANA" in n or "DTP" in n:
        return 22
    elif "TRIPLICE VIRAL" in n or "TRÍPLICE VIRAL" in n or "SCR" in n:
        return 21
    elif "TETRAVALENTE" in n or "TETRA" in n:
        return 28
    elif "POLIOMIELITE" in n or "POLIO" in n or "VIP" in n or "VOP" in n:
        return 25
    elif "ROTAVIRUS" in n or "ROTAVÍRUS" in n:
        return 40
    elif "PNEUMO" in n:
        return 42
    elif "MENINGO" in n:
        return 43
    elif "BCG" in n:
        return 10
    elif "HPV" in n:
        return 53
    elif "VARICELA" in n:
        return 45
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
    elif "4" in d and "REFOR" not in d:
        return 4
    elif "5" in d and "REFOR" not in d:
        return 5
    elif "UNICA" in d or "ÚNICA" in d:
        return 8
    elif "1" in d and "REFOR" in d:
        return 9
    elif "2" in d and "REFOR" in d:
        return 10
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
    return "" if txt.lower() in ["nan", "none", "null"] else txt

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

    # 1. Carrega dados brutos completos
    df_bruto = ler_csv(caminho_bruto).dropna(how="all")

    # 2. Cria base padronizada
    df_limpo = pd.DataFrame(index=df_bruto.index)
    df_limpo["Nome do bairro"] = "Jardim das Avenidas"

    # 3. Trata vacina, estrategia e dose
    col_ved = next((c for c in df_bruto.columns if "vacina" in c.lower()), df_bruto.columns[0])
    df_limpo["Vacina estratégia e dose"] = df_bruto[col_ved].astype(str).str.strip()

    partes = df_limpo["Vacina estratégia e dose"].apply(separar_vacina)
    df_limpo["Nome da vacina"] = [p[0] for p in partes]
    df_limpo["Estratégia"] = [p[1] for p in partes]
    df_limpo["Dose"] = [p[2] for p in partes]

    # 4. Gera codigos numericos oficiais
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

    # 8. Ordena colunas conforme padrao da sprint
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

    # 9. Salva resultado com todos os registros mantidos
    os.makedirs(PASTA_PROCESSADOS, exist_ok=True)
    df_limpo.to_csv(CAMINHO_SAIDA, index=False, encoding="utf-8")
    print(f"Salvo com sucesso: {CAMINHO_SAIDA} com {len(df_limpo)} linhas.")

if __name__ == "__main__":
    executar()