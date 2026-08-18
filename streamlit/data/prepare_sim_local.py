"""Prepara o recorte estadual para óbitos por local de ocorrência."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.constants import CAPITULOS_CID10, COD_ARARANGUA, COD_TUBARAO
from data.decode import aplica_assistmed, aplica_local
from data.load_sim import load_sc
from data.lookups import coords_municipios


@st.cache_data(show_spinner="Preparando óbitos por local de ocorrência...")
def load_local() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Devolve (SC, Araranguá ocorrência, Tubarão ocorrência)."""
    sc = _prepara(load_sc().copy())
    ara = _por_ocorrencia(sc, COD_ARARANGUA)
    tub = _por_ocorrencia(sc, COD_TUBARAO)
    return sc, ara, tub


def _prepara(df: pd.DataFrame) -> pd.DataFrame:
    """Datas, local, assistência, capítulo CID e coordenadas."""
    df = _so_ocorrencia_sc(df)
    df = _datas(df)
    df["LOCOCOR"] = aplica_local(df["LOCOCOR"])
    df["ASSISTMED"] = aplica_assistmed(df["ASSISTMED"]) if "ASSISTMED" in df else "Não informado"
    df["CAUSA_GRUPO"] = df["CAUSABAS"].map(_capitulo)
    df["IDADE_ANOS"] = pd.to_numeric(df["IDADE_ANOS"], errors="coerce")
    return _junta_coords(df)


def _so_ocorrencia_sc(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém só óbitos ocorridos em Santa Catarina (notebook)."""
    if "SC_OCORRENCIA" not in df.columns:
        return df
    flag = df["SC_OCORRENCIA"].astype(str).str.lower().isin({"true", "1"})
    return df.loc[flag].copy()


def _datas(df: pd.DataFrame) -> pd.DataFrame:
    """Garante ANO_OBITO numérico."""
    if "ANO_OBITO" in df.columns:
        df["ANO_OBITO"] = pd.to_numeric(df["ANO_OBITO"], errors="coerce")
    else:
        df["ANO_OBITO"] = pd.to_datetime(df["DTOBITO"], errors="coerce").dt.year
    return df


def _capitulo(codigo) -> str | None:
    """Primeira letra do CID-10; códigos numéricos são pré-1996."""
    if codigo is None or (isinstance(codigo, float) and pd.isna(codigo)):
        return None
    texto = str(codigo).strip()
    if texto and texto[0].isalpha():
        return CAPITULOS_CID10.get(texto[0], "Outros")
    return "Pré-CID10 (até 1995)"


def _junta_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Anexa lat/lon do município de ocorrência."""
    coords = coords_municipios().drop_duplicates("COD6")
    df["COD6"] = df["CODMUNOCOR"].astype(str).str[:6]
    return df.merge(coords, on="COD6", how="left")


def _por_ocorrencia(df: pd.DataFrame, codigo: str) -> pd.DataFrame:
    """Filtra o município pelo código IBGE de ocorrência."""
    return df.loc[df["COD6"] == codigo].copy()
