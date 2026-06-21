import requests
import pandas as pd
import matplotlib.pyplot as plt

link_api = "https://apidadosabertos.saude.gov.br/assistencia-a-saude/hospitais-e-leitos?limit=100&offset=0"

api_key = "7f5c5373ddfdf0a1b51f80ad6c1dbd01"

headers = {
    "chave-api-dados": api_key
}

parametros = {
    "limit": 100,
    "offset": 0
}

print("Fazendo requisição para API...")

resposta = requests.get(
    link_api,
    headers=headers,
    params=parametros
)

if resposta.status_code != 200:
    print("Erro na requisição")
    print("Status code:", resposta.status_code)
    print(resposta.text)
    exit()

print("Requisição realizada com sucesso")

dados = resposta.json()

print("\nTipo da resposta:")
print(type(dados))

# isinstance() verifica se uma variável é de um determinado tipo.
# Aqui estamos verificando se o JSON retornado pela API é um dicionário (dict)
# ou uma lista (list), porque APIs podem retornar estruturas diferentes.

if isinstance(dados, dict):

    print("\nChaves encontradas:")
    print(dados.keys())

    if "data" in dados:
        dados_lista = dados["data"]

    elif "results" in dados:
        dados_lista = dados["results"]

    else:
        dados_lista = None

        for valor in dados.values():
            if isinstance(valor, list):
                dados_lista = valor
                break

        if dados_lista is None:
           print("Nenhuma lista de dados encontrada no JSON.")

elif isinstance(dados, list):

    dados_lista = dados

else:
    print("Formato JSON inesperado.")

df = pd.DataFrame(dados_lista)

print("\nColunas disponíveis:")
print(df.columns.tolist())

colunas_desejadas = [
    "nome_do_hospital",
    "unidade_da_federacao_onde_fica_o_hospital",
    "nome_do_municipio_onde_fica_o_hospital",
    "descricao_do_tipo_da_unidade",
    "quantidade_total_de_leitos_do_hosptial",
    "quantidade_total_de_leitos_sus_do_hosptial",
    "quantidade_de_leitos_de_uti_do_hosptial"
]

colunas_existentes = [
    coluna for coluna in colunas_desejadas
    if coluna in df.columns
]

df = df[colunas_existentes]

mapa_colunas = {
    "nome_do_hospital": "hospital",
    "unidade_da_federacao_onde_fica_o_hospital": "uf",
    "nome_do_municipio_onde_fica_o_hospital": "municipio",
    "descricao_do_tipo_da_unidade": "tipo_unidade",
    "quantidade_total_de_leitos_do_hosptial": "leitos_totais",
    "quantidade_total_de_leitos_sus_do_hosptial": "leitos_sus",
    "quantidade_de_leitos_de_uti_do_hosptial": "leitos_uti"
}

df = df.rename(columns=mapa_colunas)


if "hospital" in df.columns:
    df = df.dropna(subset=["hospital"])

colunas_numericas = [
    "leitos_totais",
    "leitos_sus",
    "leitos_uti"
]

for coluna in colunas_numericas:

    if coluna in df.columns:

        df[coluna] = pd.to_numeric(
            df[coluna],
            # errors="coerce" faz com que valores inválidos sejam convertidos para NaN
            errors="coerce"
        )

        df[coluna] = df[coluna].fillna(0)

df = df.drop_duplicates()

print("\nPrimeiras linhas:")
print(df.head())

print("\nInformações gerais:")
print(df.info())

if "uf" in df.columns and "leitos_totais" in df.columns:

    leitos_por_uf = (
        df.groupby("uf")["leitos_totais"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nLeitos por UF:")
    print(leitos_por_uf)

    leitos_por_uf.plot(kind="bar")

    plt.title("Quantidade Total de Leitos por UF")
    plt.xlabel("UF")
    plt.ylabel("Quantidade de Leitos")

    plt.show()
