"""Decodificação de códigos SIM para rótulos legíveis."""

from __future__ import annotations

import pandas as pd

from data.constants import (
    MAPA_ASSISTMED,
    MAPA_ESC2010,
    MAPA_ESCMAE,
    MAPA_GESTACAO,
    MAPA_GRAVIDEZ,
    MAPA_LOCOCOR,
    MAPA_OBITOGRAV,
    MAPA_OBITOPARTO,
    MAPA_OBITOPUERP,
    MAPA_PARTO,
    MAPA_RACACOR,
    MAPA_SEXO,
    MAPA_TIPOBITO,
    MAPA_TPMORTEOCO,
)


def map_label(valor, mapa: dict) -> str:
    """Aplica o mapa; se já estiver decodificado, devolve o próprio texto."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "Ignorado"
    chave = _chave_codigo(valor)
    if not chave or chave.lower() in {"nan", "none", "null"}:
        return "Ignorado"
    return mapa.get(chave, chave)


def _chave_codigo(valor) -> str:
    """Normaliza 8.0 → 8 para bater no dicionário SIM."""
    chave = str(valor).strip()
    if chave.endswith(".0"):
        return chave[:-2]
    return chave


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


def aplica_assistmed(serie: pd.Series) -> pd.Series:
    """Decodifica assistência médica; vazio vira 'Não informado'."""
    return serie.map(_rotulo_assistmed)


def _rotulo_assistmed(valor) -> str:
    """Um valor de ASSISTMED em texto."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "Não informado"
    chave = str(valor).strip().replace(".0", "")
    if chave == "" or chave.lower() in {"nan", "none", "null"}:
        return "Não informado"
    return MAPA_ASSISTMED.get(chave, chave)


def aplica_mapa(serie: pd.Series, mapa: dict) -> pd.Series:
    """Aplica um mapa SIM à série, preservando texto já decodificado."""
    return serie.map(lambda v: map_label(v, mapa))


def aplica_campos_materna(df: pd.DataFrame) -> pd.DataFrame:
    """Decodifica colunas usadas na análise materna e infantil."""
    pares = (
        ("TIPOBITO", MAPA_TIPOBITO),
        ("GRAVIDEZ", MAPA_GRAVIDEZ),
        ("PARTO", MAPA_PARTO),
        ("OBITOPARTO", MAPA_OBITOPARTO),
        ("GESTACAO", MAPA_GESTACAO),
        ("OBITOPUERP", MAPA_OBITOPUERP),
        ("OBITOGRAV", MAPA_OBITOGRAV),
        ("TPMORTEOCO", MAPA_TPMORTEOCO),
        ("ESCMAE2010", MAPA_ESCMAE),
    )
    for coluna, mapa in pares:
        if coluna in df.columns:
            df[coluna] = aplica_mapa(df[coluna], mapa)
    return df
