"""Leitura do CSV analítico de vacinas."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.paths import csv_vacinas

COLS = (
    "nome_do_bairro",
    "nome_da_vacina",
    "codigo_da_vacina",
    "estrategia",
    "codigo_da_estrategia",
    "dose",
    "codigo_da_dose",
    "vacina_estrategia_e_dose",
    "lote",
    "validade_do_lote",
    "data_da_aplicacao",
    "origem",
)


@st.cache_data(show_spinner="Carregando vacinações...")
def load_vacinas() -> pd.DataFrame:
    """Base completa de aplicações de vacinas (Araranguá)."""
    caminho = csv_vacinas()
    if not caminho.exists():
        raise FileNotFoundError(
            "Base de vacinas indisponível. "
            "Confirme se `vacinas_analitico.csv` está em `data/processed/`."
        )
    existentes = set(pd.read_csv(caminho, nrows=0).columns)
    colunas = [c for c in COLS if c in existentes]
    return pd.read_csv(caminho, usecols=colunas, low_memory=False)
