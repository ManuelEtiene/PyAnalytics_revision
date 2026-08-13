"""Leitura em chunks do CSV do SIM, filtrando Araranguá."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.constants import CHUNK_SIZE, COD_ARARANGUA, COLS_RETRATO
from data.paths import csv_sim


def _colunas_disponiveis() -> list[str]:
    """Interseção entre colunas pedidas e as que existem no CSV."""
    existentes = set(pd.read_csv(csv_sim(), nrows=0).columns)
    return [col for col in COLS_RETRATO if col in existentes]


def _filtra_ararangua(bloco: pd.DataFrame) -> pd.DataFrame:
    """Mantém só residentes de Araranguá (CODMUNRES 6 dígitos)."""
    codigo = bloco["CODMUNRES"].astype(str).str[:6]
    return bloco.loc[codigo == COD_ARARANGUA]


@st.cache_data(show_spinner="Carregando óbitos de Araranguá...")
def load_ararangua() -> pd.DataFrame:
    """Lê o CSV em lotes e devolve só os óbitos de residentes locais."""
    caminho = csv_sim()
    if not caminho.exists():
        raise FileNotFoundError(
            f"CSV do SIM não encontrado em {caminho}. "
            "Coloque sim_sc_processado_analitico.csv em data/processed/."
        )
    colunas = _colunas_disponiveis()
    partes = []
    leitor = pd.read_csv(
        caminho, usecols=colunas, dtype=str, chunksize=CHUNK_SIZE
    )
    for bloco in leitor:
        partes.append(_filtra_ararangua(bloco))
    if not partes:
        return pd.DataFrame(columns=colunas)
    return pd.concat(partes, ignore_index=True)


@st.cache_data(show_spinner="Contando óbitos por município de SC...")
def load_contagem_municipios(ano_min: int, ano_max: int) -> dict:
    """Contagem de óbitos por CODMUNRES no período (toda SC)."""
    caminho = csv_sim()
    colunas = [c for c in ("DTOBITO", "CODMUNRES") if c in pd.read_csv(caminho, nrows=0).columns]
    totais: dict[str, int] = {}
    for bloco in pd.read_csv(caminho, usecols=colunas, dtype=str, chunksize=CHUNK_SIZE):
        _acumula_contagem(bloco, ano_min, ano_max, totais)
    return totais


def _acumula_contagem(bloco, ano_min: int, ano_max: int, totais: dict) -> None:
    """Soma óbitos do bloco no dicionário de totais."""
    anos = pd.to_datetime(bloco["DTOBITO"], errors="coerce").dt.year
    recorte = bloco.loc[anos.between(ano_min, ano_max)]
    contagens = recorte["CODMUNRES"].astype(str).str[:6].value_counts()
    for codigo, qtd in contagens.items():
        totais[codigo] = totais.get(codigo, 0) + int(qtd)
