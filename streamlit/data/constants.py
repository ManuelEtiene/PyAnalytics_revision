"""Constantes e mapas de decodificação do SIM."""

COD_ARARANGUA = "420140"
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
