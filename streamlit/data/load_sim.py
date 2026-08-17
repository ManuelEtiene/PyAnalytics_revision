"""Leitura em chunks do CSV do SIM, filtrando Araranguá ou SC."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.constants import CHUNK_SIZE, COD_ARARANGUA, COLS_SC, COLS_SIM
from data.paths import csv_sim


def _colunas_existentes(pedidas: tuple[str, ...]) -> list[str]:
    """Interseção entre colunas pedidas e as que existem no CSV."""
    existentes = set(pd.read_csv(csv_sim(), nrows=0).columns)
    return [col for col in pedidas if col in existentes]


def _exige_csv() -> None:
    """Interrompe se o arquivo analítico não estiver no repositório."""
    if not csv_sim().exists():
        raise FileNotFoundError(
            f"CSV do SIM não encontrado em {csv_sim()}. "
            "Coloque sim_sc_processado_analitico.csv em data/processed/."
        )


def _filtra_codigo(bloco: pd.DataFrame, coluna: str, codigo: str) -> pd.DataFrame:
    """Mantém linhas cujo código IBGE (6 dígitos) bate com o município."""
    atual = bloco[coluna].astype(str).str[:6]
    return bloco.loc[atual == codigo]


def _concatena(partes: list, colunas: list[str]) -> pd.DataFrame:
    """Une os lotes; devolve frame vazio se nada passou no filtro."""
    if not partes:
        return pd.DataFrame(columns=colunas)
    return pd.concat(partes, ignore_index=True)


def _lotes(colunas: list[str]):
    """Itera o CSV em chunks só com as colunas pedidas."""
    return pd.read_csv(
        csv_sim(), usecols=colunas, dtype=str, chunksize=CHUNK_SIZE
    )


@st.cache_data(show_spinner="Carregando óbitos de Araranguá...")
def load_ararangua() -> pd.DataFrame:
    """Óbitos de residentes de Araranguá (CODMUNRES)."""
    return _load_municipio("CODMUNRES", COD_ARARANGUA, COLS_SIM)


@st.cache_data(show_spinner="Carregando óbitos ocorridos em Araranguá...")
def load_ocorrencia_ararangua() -> pd.DataFrame:
    """Óbitos cuja ocorrência foi em Araranguá (CODMUNOCOR)."""
    return _load_municipio("CODMUNOCOR", COD_ARARANGUA, COLS_SIM)


def _load_municipio(coluna: str, codigo: str, pedidas: tuple[str, ...]) -> pd.DataFrame:
    """Lê o CSV e filtra um município pela coluna de código IBGE."""
    _exige_csv()
    colunas = _colunas_existentes(pedidas)
    partes = [_filtra_codigo(bloco, coluna, codigo) for bloco in _lotes(colunas)]
    return _concatena(partes, colunas)


@st.cache_data(show_spinner="Carregando óbitos de Santa Catarina...")
def load_sc() -> pd.DataFrame:
    """Recorte estadual usado nos gráficos comparativos de local."""
    _exige_csv()
    colunas = _colunas_existentes(COLS_SC)
    return _concatena(list(_lotes(colunas)), colunas)


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
