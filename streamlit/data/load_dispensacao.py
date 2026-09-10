"""Leitura do CSV de dispensação de medicamentos."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.paths import csv_dispensacao

COLS = (
    "data",
    "quantidade",
    "custo_medio",
    "saida",
    "material_nome_base",
    "material_nome",
    "material_tipo",
    "material_descricao_complementar",
    "classe_terapeutica",
    "tipo_tratamento",
    "fabricante_nome",
    "bairro_nome",
    "centro_custo_nome",
    "ups_nome",
)


@st.cache_data(show_spinner="Carregando dispensação de medicamentos...")
def load_dispensacao() -> pd.DataFrame:
    """Base completa de dispensação (Farmácia Básica)."""
    caminho = csv_dispensacao()
    if not caminho.exists():
        raise FileNotFoundError(
            "Base de medicamentos indisponível. "
            "Confirme se `dispensacao_analitico.csv` está em `data/processed/` "
            "(arquivo real, não atalho/symlink)."
        )
    existentes = set(pd.read_csv(caminho, nrows=0).columns)
    colunas = [c for c in COLS if c in existentes]
    return pd.read_csv(caminho, usecols=colunas, low_memory=False)
