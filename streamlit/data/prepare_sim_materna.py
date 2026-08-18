"""Prepara óbitos infantis e maternos de residentes de Araranguá."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.decode import aplica_campos_materna
from data.lookups import mapa_cbo
from data.prepare_sim_retrato import load_retrato


@st.cache_data(show_spinner="Preparando saúde materna e infantil...")
def load_materna() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (óbitos infantis < 10 anos, óbitos maternos)."""
    df = aplica_campos_materna(load_retrato().copy())
    _numericos(df)
    _faixas(df)
    if "OCUPMAE" in df.columns:
        cbo = mapa_cbo()
        df["OCUPMAE"] = df["OCUPMAE"].map(lambda c: _ocup_mae(c, cbo))
    infantil = df.loc[df["IDADE_ANOS"] < 10].copy()
    return infantil, _materno(df)


def _numericos(df: pd.DataFrame) -> None:
    """Converte peso, semanas e idade da mãe; descarta gestação > 42."""
    for col in ("PESO", "SEMAGESTAC", "IDADEMAE", "IDADE_ANOS"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "SEMAGESTAC" in df.columns:
        df.loc[df["SEMAGESTAC"] > 42, "SEMAGESTAC"] = None


def _faixas(df: pd.DataFrame) -> None:
    """Faixas de peso, idade da mãe e semanas — iguais ao notebook."""
    df["FAIXA_PESO"] = pd.cut(
        df["PESO"],
        bins=[-1, 0.1, 1000, 3000, 10000],
        labels=["Zero/Nulo", "Até 1kg", "1kg a 3kg", "Mais de 3kg"],
    )
    df["FAIXA_IDADEMAE"] = pd.cut(
        df["IDADEMAE"],
        bins=[-1, 0.1, 19, 34, 100],
        labels=["Zero/Nulo", "até 19 anos", "20 a 34 anos", "35 ou mais"],
    )
    df["FAIXA_SEMAGESTAC"] = pd.cut(
        df["SEMAGESTAC"],
        bins=[-1, 0.1, 10, 21, 36, 38, 100],
        labels=[
            "Zero/Nulo", "até 10 semanas", "11 a 21 semanas",
            "22 a 36 semanas", "37 a 38 semanas", "39 ou mais",
        ],
    )


def _materno(df: pd.DataFrame) -> pd.DataFrame:
    """Mulheres com TPMORTEOCO no ciclo gravídico-puerperal."""
    fora = {"Não ocorreu nesses períodos", "Ignorado"}
    mascara = (
        (df["SEXO"] == "Feminino")
        & df["TPMORTEOCO"].notna()
        & ~df["TPMORTEOCO"].isin(fora)
    )
    return df.loc[mascara].copy()


def _ocup_mae(codigo, mapa: dict) -> str:
    """CBO da mãe ou o próprio código se não houver nome."""
    if codigo is None or (isinstance(codigo, float) and pd.isna(codigo)):
        return "Ignorado"
    chave = str(codigo).strip().zfill(6)
    if chave in {"999999", "000000"}:
        return "Ignorado"
    return mapa.get(chave, str(codigo))
