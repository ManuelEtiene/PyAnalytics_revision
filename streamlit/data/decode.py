"""Decodificação de códigos SIM para rótulos legíveis."""

from __future__ import annotations

import pandas as pd

from data.constants import MAPA_ESC2010, MAPA_LOCOCOR, MAPA_RACACOR, MAPA_SEXO


def map_label(valor, mapa: dict) -> str:
    """Aplica o mapa; se já estiver decodificado, devolve o próprio texto."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "Ignorado"
    chave = str(valor).strip()
    if chave == "" or chave.lower() in {"nan", "none", "null"}:
        return "Ignorado"
    return mapa.get(chave, chave)


def decodifica_causa(codigo, mapa_cid: dict) -> str:
    """Usa os 3 primeiros caracteres do CID-10 (categoria)."""
    if codigo is None or (isinstance(codigo, float) and pd.isna(codigo)):
        return "Ignorado"
    cod = str(codigo).strip().upper()
    if not cod:
        return "Ignorado"
    return mapa_cid.get(cod[:3], f"Desconhecido ({cod})")


def decodifica_municipio(codigo, mapa_mun: dict) -> str:
    """Converte código IBGE de 6 dígitos no nome do município."""
    if codigo is None or (isinstance(codigo, float) and pd.isna(codigo)):
        return "Ignorado"
    cod6 = str(codigo).strip().zfill(6)[:6]
    return mapa_mun.get(cod6, f"Desconhecido ({cod6})")


def decodifica_ocupacao(codigo, mapa_cbo: dict) -> str:
    """Converte CBO-2002; 000000/999999 viram ignorado."""
    if codigo is None or (isinstance(codigo, float) and pd.isna(codigo)):
        return "Ignorado/Não se aplica"
    cod = str(codigo).strip().zfill(6)
    if cod in {"999999", "000000", "00nan0"}:
        return "Ignorado/Não se aplica"
    return mapa_cbo.get(cod, f"Desconhecido ({cod})")


def aplica_sexo(serie: pd.Series) -> pd.Series:
    """Decodifica sexo."""
    return serie.map(lambda v: map_label(v, MAPA_SEXO))


def aplica_raca(serie: pd.Series) -> pd.Series:
    """Decodifica raça/cor."""
    return serie.map(lambda v: map_label(v, MAPA_RACACOR))


def aplica_esc(serie: pd.Series) -> pd.Series:
    """Decodifica escolaridade (ESC2010)."""
    return serie.map(lambda v: map_label(v, MAPA_ESC2010))


def aplica_local(serie: pd.Series) -> pd.Series:
    """Decodifica local de ocorrência."""
    return serie.map(lambda v: map_label(v, MAPA_LOCOCOR))
