"""Prepara mortalidade evitável e desigualdades sociais (Araranguá)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.constants import (
    COD_ARARANGUA,
    COD_CRICIUMA,
    FAIXAS_INFARTO,
    POP_CENSO_2022,
    ROTULOS_FAIXAS_INFARTO,
)
from data.load_sim import load_sc
from data.prepare_sim_retrato import load_retrato


def classificar_grupo_causa(causa) -> str:
    """Agrupa CAUSABAS em capítulos CID-10 (notebook Sprint 1)."""
    if causa is None or (isinstance(causa, float) and pd.isna(causa)):
        return "Mal Definidos / Ignorados"
    texto = str(causa).strip().upper()
    if not texto:
        return "Mal Definidos / Ignorados"
    letra = texto[0]
    if letra in {"A", "B"}:
        return "Infecciosas e Parasitárias"
    if letra in {"C", "D"}:
        return "Neoplasias (Tumores)"
    if letra == "E":
        return "Endócrinas e Metabólicas (ex: Diabetes)"
    if letra == "I":
        return "Doenças do Aparelho Circulatório"
    if letra == "J":
        return "Doenças do Aparelho Respiratório"
    if letra == "K":
        return "Doenças do Aparelho Digestivo"
    if letra in {"V", "W", "X", "Y"}:
        return "Causas Externas (Acidentes/Violências)"
    if letra == "R":
        return "Sintomas e Sinais Mal Definidos"
    return "Outras Causas Específicas"


@st.cache_data(show_spinner="Preparando mortalidade evitável...")
def load_evitavel() -> pd.DataFrame:
    """Óbitos de Araranguá com grupo de causa e faixa do infarto."""
    df = load_retrato().copy()
    df["GRUPO_CAUSA"] = df["CAUSABAS"].map(classificar_grupo_causa)
    df["FAIXA_INFARTO"] = pd.cut(
        df["IDADE_ANOS"],
        bins=FAIXAS_INFARTO,
        labels=ROTULOS_FAIXAS_INFARTO,
        right=True,
    )
    return df


@st.cache_data(show_spinner="Calculando taxas territoriais...")
def taxas_por_grupo() -> pd.DataFrame:
    """Média anual de óbitos/100 mil por grupo (Ara × Criciúma × SC)."""
    sc = load_sc().copy()
    sc["GRUPO_CAUSA"] = sc["CAUSABAS"].map(classificar_grupo_causa)
    anos = _anos_periodo(sc)
    return pd.DataFrame(
        {
            "Araranguá": _taxa(_filtra_res(sc, COD_ARARANGUA), anos, "Araranguá"),
            "Criciúma": _taxa(_filtra_res(sc, COD_CRICIUMA), anos, "Criciúma"),
            "Santa Catarina": _taxa(sc, anos, "SC (total)"),
        }
    ).fillna(0)


def _filtra_res(df: pd.DataFrame, codigo: str) -> pd.DataFrame:
    """Residentes do município (CODMUNRES)."""
    cod = df["CODMUNRES"].astype(str).str[:6]
    return df.loc[cod == codigo]


def _anos_periodo(df: pd.DataFrame) -> int:
    """Quantidade de anos distintos no recorte."""
    if "ANO_OBITO" in df.columns:
        anos = pd.to_numeric(df["ANO_OBITO"], errors="coerce").dropna()
    else:
        anos = pd.to_datetime(df["DTOBITO"], errors="coerce").dt.year.dropna()
    return max(int(anos.nunique()), 1)


def _taxa(df: pd.DataFrame, anos: int, pop_chave: str) -> pd.Series:
    """Contagem do grupo → média anual por 100 mil habitantes."""
    pop = POP_CENSO_2022[pop_chave]
    contagem = df["GRUPO_CAUSA"].value_counts()
    return (contagem / anos / pop * 100_000).round(2)
