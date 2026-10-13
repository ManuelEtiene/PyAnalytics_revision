"""Nomes curtos e legíveis das vacinas (eixo/legenda)."""

from __future__ import annotations

import re

# Nome original → rótulo curto no gráfico
_MAPA = {
    "Vacina influenza trivalente": "Influenza",
    "Vacina difteria e tétano adulto": "dT adulto",
    "Vacina hepatite B": "Hepatite B",
    "Vacina dengue (atenuada)": "Dengue",
    "Vacina dengue": "Dengue",
    "Vacina polio injetável (inativada poliomielite)": "Pólio injetável",
    "Vacina polio injetável": "Pólio injetável",
    "Vacina febre amarela": "Febre amarela",
    "Vacina sarampo, caxumba, rubéola": "SCR",
    "Vacina sarampo, caxumba, rubéola e varicela": "SCR-V",
    "Vacina penta (DTP/HepB/Hib)": "Penta",
    "Vacina penta": "Penta",
    "Vacina pneumo 10": "Pneumo 10",
    "Vacina pneumo 13": "Pneumo 13",
    "Vacina pneumo 23": "Pneumo 23",
    "Vacina Pneumo 20": "Pneumo 20",
    "Vacina meningo ACWY": "Meningo ACWY",
    "Vacina meningo C": "Meningo C",
    "Vacina varicela": "Varicela",
    "Vacina rotavírus": "Rotavírus",
    "Vacina DTP": "DTP",
    "Vacina DTPa infantil": "DTPa infantil",
    "Vacina dTpa adulto": "dTpa adulto",
    "Vacina HPV quadrivalente": "HPV",
    "Vacina COVID-19-RNAm, Pfizer (Comirnaty)": "COVID-19 Pfizer",
    "Vacina COVID-19-RNAm, Pfizer (Comirnaty) pediátrica menor de 5 anos": "COVID-19 Pfizer <5a",
    "Vacina COVID-19-RNAm, Pfizer (Comirnaty) pediátrica menor de": "COVID-19 Pfizer ped.",
    "Vacina COVID": "COVID-19",
    "Vacina hepatite A infantil": "Hepatite A infantil",
    "Vacina hepatite A adulto": "Hepatite A adulto",
    "Vacina raiva em cultivo celular vero": "Raiva",
    "Vacina Vírus Sincicial A e B (recombinante)": "VSR A e B",
    "Vacina Vírus Sincicial A e B": "VSR A e B",
    "Vacina vírus sincicial respiratório (recombinante, adjuvada)": "VSR adjuvada",
    "Vacina BCG": "BCG",
    "Vacina Hib": "Hib",
    "Vacina hexa (DTPa/HepB/VIP/Hib)": "Hexa",
    "NIRSEVIMABE 0,5ml": "Nirsevimabe 0,5 ml",
    "NIRSEVIMABE 1,0ml": "Nirsevimabe 1,0 ml",
}


def nome_vacina_curto(nome) -> str:
    """Padroniza o nome da vacina para eixo e legenda."""
    if nome is None or (isinstance(nome, float) and str(nome) == "nan"):
        return "Não informado"
    texto = str(nome).strip()
    if not texto:
        return "Não informado"
    if texto in _MAPA:
        return _MAPA[texto]
    # Linhas malformadas: "Vacina SCR (24) - Rotina (1) - 2ª DOSE"
    if re.search(r"sarampo,\s*caxumba,\s*rub[eé]ola", texto, re.I):
        if re.search(r"varicela", texto, re.I):
            return "SCR-V"
        return "SCR"
    if re.search(r"nirsevimabe", texto, re.I):
        return "Nirsevimabe"
    # Fallback: tira prefixo e detalhes entre parênteses longos
    limpo = re.sub(r"^Vacina\s+", "", texto, flags=re.I)
    limpo = re.sub(r"\s+", " ", limpo).strip()
    return limpo if limpo else texto


def legenda_vacinas(originais) -> dict[str, str]:
    """Mapa rótulo curto → nome original (para legenda quando abreviado)."""
    mapa: dict[str, str] = {}
    for original in originais:
        curto = nome_vacina_curto(original)
        if curto not in mapa:
            mapa[curto] = str(original)
    return mapa
