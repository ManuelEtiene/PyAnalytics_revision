"""Leitura do CSV da REMUME (lista municipal de medicamentos)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.paths import csv_remume

COLS = (
    "id",
    "item",
    "categoria",
    "medicamento",
    "nome_busca",
    "apresentacao",
    "local_bruto",
    "locais",
    "qtd_locais",
    "tem_farmacia",
    "tem_ubs",
    "observacao",
)


@st.cache_data(show_spinner="Carregando REMUME...")
def load_remume() -> pd.DataFrame:
    """Base processada da REMUME de Araranguá."""
    caminho = csv_remume()
    if not caminho.exists():
        raise FileNotFoundError(
            "Base REMUME indisponível. "
            "Rode `python src/data/processar_remume.py` "
            "para gerar `data/processed/remume.csv`."
        )
    existentes = set(pd.read_csv(caminho, nrows=0).columns)
    colunas = [c for c in COLS if c in existentes]
    return pd.read_csv(caminho, usecols=colunas, low_memory=False)
