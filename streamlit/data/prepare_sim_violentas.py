"""Prepara mortes violentas ocorridas em Araranguá (CID V–Y)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.cid_sim_violentas import tipo_violencia, traduz_cid_violenta
from data.decode import aplica_assistmed, aplica_local
from data.load_sim import load_ocorrencia_ararangua, load_sc
from data.lookups import mapa_municipios, mapa_populacao


@st.cache_data(show_spinner="Preparando mortes violentas...")
def load_violentas() -> pd.DataFrame:
    """Óbitos violentos com ocorrência em Araranguá e local preenchido."""
    df = load_ocorrencia_ararangua().copy()
    df = df.loc[_mascara_violenta(df["CAUSABAS"])].dropna(subset=["LOCOCOR"])
    df["LOCOCOR"] = aplica_local(df["LOCOCOR"])
    df["ASSISTMED"] = aplica_assistmed(df["ASSISTMED"])
    df["IDADE_ANOS"] = pd.to_numeric(df["IDADE_ANOS"], errors="coerce")
    df["CAUSA_DESC"] = df["CAUSABAS"].map(traduz_cid_violenta)
    df["TIPO_VIOLENCIA"] = df["CAUSABAS"].map(tipo_violencia)
    df["ANO_OBITO"] = pd.to_numeric(df.get("ANO_OBITO"), errors="coerce")
    return df


@st.cache_data(show_spinner="Calculando taxas violentas em SC...")
def ranking_taxa_sc() -> pd.Series:
    """Taxa de mortes violentas por 100 mil hab. (ocorrência, SC)."""
    sc = load_sc()
    violentos = sc.loc[_mascara_violenta(sc["CAUSABAS"])]
    if "SC_OCORRENCIA" in violentos.columns:
        flag = violentos["SC_OCORRENCIA"].astype(str).str.lower().isin({"true", "1"})
        violentos = violentos.loc[flag]
    return _taxas(violentos)


def _mascara_violenta(serie: pd.Series) -> pd.Series:
    """CID de causas externas (V–Y)."""
    return serie.astype(str).str.match(r"^[V-Y]", na=False)


def _taxas(df: pd.DataFrame) -> pd.Series:
    """Contagem por município / população × 100 mil."""
    contagem = df["CODMUNOCOR"].astype(str).str[:6].value_counts()
    pop = mapa_populacao()
    nomes = mapa_municipios()
    taxas = {}
    for codigo, n in contagem.items():
        habitantes = pop.get(str(codigo).zfill(6)[:6])
        if habitantes and habitantes > 0:
            taxas[nomes.get(codigo, codigo)] = n / habitantes * 100_000
    return pd.Series(taxas).sort_values(ascending=False)
