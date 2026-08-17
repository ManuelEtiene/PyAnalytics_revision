"""Download e cache local das tabelas de lookup (CID, IBGE, CBO)."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
import streamlit as st

from data.paths import cache_dir

CID_URL = (
    "https://raw.githubusercontent.com/cleytonferrari/CidDataSus/"
    "master/CIDImport/Repositorio/Resources/CID-10-CATEGORIAS.CSV"
)
MUN_URL = (
    "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/"
    "main/csv/municipios.csv"
)
POP_URL = (
    "https://raw.githubusercontent.com/mapaslivres/municipios-br/"
    "main/tabelas/municipios.csv"
)
CBO_URL = (
    "https://raw.githubusercontent.com/lucassmacedo/cbo-brasil/"
    "master/csv/CBO2002%20-%20Ocupacao.csv"
)


def _baixa(url: str, destino: Path) -> Path | None:
    """Baixa o arquivo se ainda não existir no cache."""
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    try:
        urlretrieve(url, destino)
        return destino
    except Exception:
        return None


@st.cache_data(show_spinner="Carregando tabela CID-10...")
def mapa_cid10() -> dict:
    """Categoria CID-10 (3 letras) → descrição."""
    path = _baixa(CID_URL, cache_dir() / "cid10.csv")
    if path is None:
        return {}
    try:
        cid = pd.read_csv(path, sep=";", encoding="latin1")
        cid["CAT"] = cid["CAT"].astype(str).str.strip().str.upper()
        return dict(zip(cid["CAT"], cid["DESCRICAO"]))
    except Exception:
        return {}


@st.cache_data(show_spinner="Carregando municípios IBGE...")
def mapa_municipios() -> dict:
    """Código IBGE 6 dígitos → nome do município."""
    path = _baixa(MUN_URL, cache_dir() / "municipios.csv")
    if path is None:
        return {}
    try:
        mun = pd.read_csv(path)
        mun["COD6"] = mun["codigo_ibge"].astype(str).str[:6]
        return dict(zip(mun["COD6"], mun["nome"]))
    except Exception:
        return {}


@st.cache_data(show_spinner="Carregando população municipal...")
def mapa_populacao() -> dict:
    """Código IBGE 6 dígitos → população 2021 (IBGE)."""
    path = _baixa(POP_URL, cache_dir() / "populacao.csv")
    if path is None:
        return {}
    try:
        pop = pd.read_csv(path, dtype=str)
        pop["COD6"] = pop["municipio"].astype(str).str[:6]
        return dict(zip(pop["COD6"], pd.to_numeric(pop["pop_21"], errors="coerce")))
    except Exception:
        return {}


@st.cache_data(show_spinner="Carregando coordenadas municipais...")
def coords_municipios() -> pd.DataFrame:
    """Código IBGE 6 dígitos, nome, latitude e longitude."""
    path = _baixa(MUN_URL, cache_dir() / "municipios.csv")
    if path is None:
        return pd.DataFrame(columns=["COD6", "nome", "lat", "lon"])
    mun = pd.read_csv(path)
    mun["COD6"] = mun["codigo_ibge"].astype(str).str[:6]
    return mun.rename(columns={"latitude": "lat", "longitude": "lon"})[
        ["COD6", "nome", "lat", "lon"]
    ]


@st.cache_data(show_spinner="Carregando ocupações CBO...")
def mapa_cbo() -> dict:
    """Código CBO-2002 → nome da ocupação."""
    path = _baixa(CBO_URL, cache_dir() / "cbo.csv")
    if path is None:
        return {}
    try:
        cbo = pd.read_csv(path, sep=";", encoding="utf-8")
        cbo["code"] = cbo["code"].astype(str).str.zfill(6)
        return dict(zip(cbo["code"], cbo["name"]))
    except Exception:
        return {}
