"""Constantes e mapas de decodificação do SIM."""

COD_ARARANGUA = "420140"
COD_TUBARAO = "420830"
CHUNK_SIZE = 200_000

MAPA_SEXO = {
    "1": "Masculino",
    "2": "Feminino",
    "0": "Ignorado",
    "9": "Ignorado",
    "M": "Masculino",
    "F": "Feminino",
    "I": "Ignorado",
}

MAPA_RACACOR = {
    "1": "Branca",
    "2": "Preta",
    "3": "Amarela",
    "4": "Parda",
    "5": "Indigena",
    "9": "Ignorado",
}

MAPA_ESC2010 = {
    "0": "Sem escolaridade",
    "1": "Fundamental I (1a a 4a serie)",
    "2": "Fundamental II (5a a 8a serie)",
    "3": "Medio (antigo 2o Grau)",
    "4": "Superior incompleto",
    "5": "Superior completo",
    "9": "Ignorado",
}

MAPA_LOCOCOR = {
    "1": "Hospital",
    "2": "Outros estabelecimentos de saude",
    "3": "Domicilio",
    "4": "Via publica",
    "5": "Outros",
    "6": "Aldeia indigena",
    "9": "Ignorado",
    "Outro estabelecimento de saude": "Outros estabelecimentos de saude",
}

MAPA_ESC_CURTO = {
    "Sem escolaridade": "Sem esc.",
    "Fundamental I (1a a 4a serie)": "Fund. I",
    "Fundamental II (5a a 8a serie)": "Fund. II",
    "Medio (antigo 2o Grau)": "Médio",
    "Superior incompleto": "Sup. incompleto",
    "Superior completo": "Sup. completo",
    "Ignorado": "Ignorado",
}

MAPA_LOCAL_CURTO = {
    "Hospital": "Hospital",
    "Outros estabelecimentos de saude": "OES",
    "Domicilio": "Domicílio",
    "Via publica": "Via pública",
    "Outros": "Outros",
    "Aldeia indigena": "Aldeia indíg.",
    "Ignorado": "Ignorado",
}

ORDEM_ESC = (
    "Sem escolaridade",
    "Fundamental I (1a a 4a serie)",
    "Fundamental II (5a a 8a serie)",
    "Medio (antigo 2o Grau)",
    "Superior incompleto",
    "Superior completo",
)

FAIXAS = [0, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 200]
ROTULOS_FAIXAS = (
    "<1", "1-9", "10-19", "20-29", "30-39", "40-49",
    "50-59", "60-69", "70-79", "80-89", "90+",
)

NOMES_MESES = (
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
)

COLS_RETRATO = (
    "DTOBITO", "IDADE_ANOS", "SEXO", "RACACOR", "ESC2010",
    "CODMUNRES", "CODMUNOCOR", "LOCOCOR", "CAUSABAS", "OCUP",
)

COLS_TEMAS = (
    "ASSISTMED", "TIPOBITO", "IDADEMAE", "ESCMAE2010", "GRAVIDEZ",
    "PARTO", "OBITOPARTO", "PESO", "OCUPMAE", "GESTACAO",
    "SEMAGESTAC", "TPMORTEOCO", "OBITOGRAV", "OBITOPUERP", "ANO_OBITO",
)

COLS_SIM = COLS_RETRATO + COLS_TEMAS

COLS_SC = (
    "DTOBITO", "ANO_OBITO", "IDADE_ANOS", "LOCOCOR", "ASSISTMED",
    "CAUSABAS", "CODMUNOCOR", "CODMUNRES", "SC_OCORRENCIA",
)

MAPA_ASSISTMED = {
    "1": "Sim",
    "2": "Não",
    "9": "Ignorado",
    "0": "Ignorado",
}

MAPA_TIPOBITO = {"1": "Óbito Fetal", "2": "Óbito Não Fetal"}

MAPA_GRAVIDEZ = {
    "0": "Ignorado",
    "1": "Única",
    "2": "Dupla (Gêmeos)",
    "3": "Tripla ou mais",
    "9": "Ignorado",
}

MAPA_PARTO = {
    "0": "Ignorado",
    "1": "Vaginal (Normal)",
    "2": "Cesáreo",
    "3": "Ignorado",
    "9": "Ignorado",
}

MAPA_OBITOPARTO = {
    "1": "Antes do Parto",
    "2": "Durante o Parto",
    "3": "Depois do Parto",
    "9": "Ignorado",
}

MAPA_GESTACAO = {
    "0": "Ignorado",
    "1": "Menos de 22 semanas",
    "2": "22 a 27 semanas",
    "3": "28 a 31 semanas",
    "4": "32 a 36 semanas",
    "5": "37 a 41 semanas",
    "6": "42 semanas e mais",
    "8": "Não classificado",
    "9": "Ignorado",
}

MAPA_OBITOPUERP = {
    "1": "Sim, até 42 dias",
    "2": "Sim, de 43 dias a 1 ano",
    "3": "Não",
    "9": "Ignorado",
}

MAPA_OBITOGRAV = {"1": "Sim", "2": "Não", "9": "Ignorado"}

MAPA_TPMORTEOCO = {
    "1": "Na gravidez",
    "2": "No parto",
    "3": "No abortamento",
    "4": "Até 42 dias após o parto",
    "5": "De 43 dias a 1 ano após o parto",
    "8": "Não ocorreu nesses períodos",
    "9": "Ignorado",
}

MAPA_ESCMAE = {
    "0": "Sem",
    "1": "Fund. I",
    "2": "Fund. II",
    "3": "Médio",
    "4": "Sup. incomp.",
    "5": "Sup. comp.",
    "9": "Ignorado",
}

CAPITULOS_CID10 = {
    "A": "Infecciosas/parasitárias",
    "B": "Infecciosas/parasitárias",
    "C": "Neoplasias",
    "D": "Neoplasias/sangue",
    "E": "Endócrinas/metabólicas",
    "F": "Mentais/comportamentais",
    "G": "Sistema nervoso",
    "H": "Olhos/ouvidos",
    "I": "Circulatório",
    "J": "Respiratório",
    "K": "Digestivo",
    "L": "Pele",
    "M": "Osteomuscular",
    "N": "Geniturinário",
    "O": "Gravidez/parto",
    "P": "Perinatal",
    "Q": "Malformações congênitas",
    "R": "Sintomas mal definidos",
    "S": "Causas externas (lesões)",
    "T": "Causas externas (lesões)",
    "V": "Causas externas (acidentes/violência)",
    "W": "Causas externas (acidentes/violência)",
    "X": "Causas externas (acidentes/violência)",
    "Y": "Causas externas (acidentes/violência)",
    "Z": "Fatores que influenciam o estado de saúde",
    "U": "Outros/códigos especiais",
}

POP_CENSO_2022 = {
    "Araranguá": 71_922,
    "Tubarão": 110_088,
    "SC (total)": 7_610_361,
}

POP_ARARANGUA_VIOLENTAS = 107_089

# Nomes de coluna SIM → rótulo de eixo/legenda (evita FAIXA_ETARIA cru)
ROTULO_COLUNA = {
    "FAIXA_ETARIA": "Faixa etária",
    "FAIXA_PESO": "Faixa de peso",
    "FAIXA_IDADEMAE": "Idade da mãe",
    "FAIXA_SEMAGESTAC": "Semanas de gestação",
    "ESC2010": "Escolaridade",
    "ESCMAE2010": "Escolaridade da mãe",
    "CAUSABAS_DESC": "Causa básica",
    "CAUSA_DESC": "Causa",
    "CAUSA_GRUPO": "Grupo de causa",
    "PARTO": "Tipo de parto",
    "GRAVIDEZ": "Tipo de gravidez",
    "GESTACAO": "Tempo de gestação",
    "SEMAGESTAC": "Semanas de gestação",
    "TIPOBITO": "Tipo de óbito",
    "ASSISTMED": "Assistência médica",
    "OBITOPARTO": "Momento do óbito",
    "LOCOCOR": "Local de ocorrência",
    "IDADE_ANOS": "Idade (anos)",
    "IDADEMAE": "Idade da mãe",
    "PESO": "Peso (g)",
    "SEXO": "Sexo",
    "RACACOR": "Raça/cor",
    "OCUP": "Ocupação",
    "OCUPMAE": "Ocupação da mãe",
    "ANO_OBITO": "Ano do óbito",
    "TIPO_VIOLENCIA": "Tipo de violência",
}


def rotulo_coluna(nome) -> str:
    """Troca NOME_TECNICO por rótulo em português."""
    chave = "" if nome is None else str(nome).strip()
    if not chave or chave == "None":
        return ""
    if chave in ROTULO_COLUNA:
        return ROTULO_COLUNA[chave]
    if chave.isupper() and any(c.isalpha() for c in chave):
        return chave.replace("_", " ").capitalize()
    return chave


ORDEM_ASSIST = ("Sim", "Não", "Ignorado", "Não informado")
ORDEM_LOCAIS_BOX = (
    "Hospital",
    "Domicilio",
    "Via publica",
    "Outros",
    "Outros estabelecimentos de saude",
)
