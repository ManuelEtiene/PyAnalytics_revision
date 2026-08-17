"""Prepara o recorte de Araranguá para os gráficos do Retrato."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.constants import FAIXAS, ROTULOS_FAIXAS
from data.decode import (
    aplica_assistmed,
    aplica_esc,
    aplica_local,
    aplica_raca,
    aplica_sexo,
    decodifica_causa,
    decodifica_municipio,
    decodifica_ocupacao,
)
from data.load_sim import load_ararangua
from data.lookups import mapa_cbo, mapa_cid10, mapa_municipios


def _preenche_datas(df: pd.DataFrame) -> pd.DataFrame:
    """Converte DTOBITO e deriva ano/mês (linhas sem data válida ficam NaT)."""
    df["DTOBITO_DT"] = pd.to_datetime(df["DTOBITO"], errors="coerce")
    df["ANO_OBITO"] = df["DTOBITO_DT"].dt.year
    df["MES_OBITO"] = df["DTOBITO_DT"].dt.month
    return df


def _preenche_categorias(df: pd.DataFrame, cid: dict) -> pd.DataFrame:
    """Aplica rótulos de sexo, raça, escolaridade, local e causa."""
    df["SEXO"] = aplica_sexo(df["SEXO"])
    df["RACACOR"] = aplica_raca(df["RACACOR"])
    df["ESC2010"] = aplica_esc(df["ESC2010"]) if "ESC2010" in df else "Ignorado"
    df["LOCOCOR"] = aplica_local(df["LOCOCOR"])
    if "ASSISTMED" in df.columns:
        df["ASSISTMED"] = aplica_assistmed(df["ASSISTMED"])
    df["CAUSABAS_DESC"] = df["CAUSABAS"].map(lambda c: decodifica_causa(c, cid))
    return df


def _preenche_idade(df: pd.DataFrame) -> pd.DataFrame:
    """Garante idade em anos e faixa etária (idade ausente fica fora das faixas)."""
    df["IDADE_ANOS"] = pd.to_numeric(df.get("IDADE_ANOS"), errors="coerce")
    df["FAIXA_ETARIA"] = pd.cut(
        df["IDADE_ANOS"], bins=FAIXAS, labels=ROTULOS_FAIXAS, right=False
    )
    return df


def _preenche_territorio(df: pd.DataFrame, mun: dict) -> pd.DataFrame:
    """Nomes de município e flag de óbito fora da residência."""
    df["CODMUNRES_NOME"] = df["CODMUNRES"].map(lambda c: decodifica_municipio(c, mun))
    if "CODMUNOCOR" not in df.columns:
        df["CODMUNOCOR"] = df["CODMUNRES"]
    df["CODMUNOCOR_NOME"] = df["CODMUNOCOR"].map(lambda c: decodifica_municipio(c, mun))
    res = df["CODMUNRES"].astype(str).str.zfill(6).str[:6]
    ocor = df["CODMUNOCOR"].astype(str).str.zfill(6).str[:6]
    df["OCORREU_FORA_RESIDENCIA"] = res != ocor
    return df


def _preenche_ocupacao(df: pd.DataFrame, cbo: dict) -> pd.DataFrame:
    """Descrição da ocupação, se a coluna existir."""
    if "OCUP" not in df.columns:
        return df
    df["OCUPACAO_DESC"] = df["OCUP"].map(lambda c: decodifica_ocupacao(c, cbo))
    return df


@st.cache_data(show_spinner="Preparando indicadores do Retrato...")
def load_retrato() -> pd.DataFrame:
    """DataFrame pronto para os gráficos do Retrato da mortalidade."""
    df = load_ararangua().copy()
    df = _preenche_datas(df)
    df = _preenche_categorias(df, mapa_cid10())
    df = _preenche_idade(df)
    df = _preenche_territorio(df, mapa_municipios())
    return _preenche_ocupacao(df, mapa_cbo())


def periodo_titulo(df: pd.DataFrame) -> str:
    """Texto '1992-2025' (ou um único ano)."""
    anos = df["ANO_OBITO"].dropna()
    if anos.empty:
        return "sem período"
    minimo, maximo = int(anos.min()), int(anos.max())
    return f"{minimo}-{maximo}" if minimo != maximo else str(minimo)
