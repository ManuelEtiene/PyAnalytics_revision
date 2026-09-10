"""Prepara a base de dispensação (custos, destaques, bairro, tempo e perfis)."""

from __future__ import annotations

import unicodedata

import pandas as pd
import streamlit as st

from data.load_dispensacao import load_dispensacao
from data.med_perfis_map import MAPA_PERFIS, PERFIL_OUTROS
from data.paths import csv_censo_bairros

_PLACEHOLDERS = {
    "NAO INFORMADO",
    "NAO SABE INFORMAR",
    "BAIRRO NAO INFORMADO NO CADSUS",
    "ZERO",
    "DISTRITO",
    "ARARANGUA",
}

_CORRECAO = {
    "ALTO FELZ": "ALTO FELIZ",
    "CIADADE ALTA": "CIDADE ALTA",
    "CIDADA ALTA": "CIDADE ALTA",
    "CIDADEA ALTA": "CIDADE ALTA",
    "COLONIHNA": "COLONINHA",
    "COLOONINHA": "COLONINHA",
    "COLONINHA 05/133": "COLONINHA",
    "COLONINHA 135/04": "COLONINHA",
    "COLONINHA 141/04": "COLONINHA",
    "COLONINHA 55/80": "COLONINHA",
    "COLONINHA I": "COLONINHA",
    "COLONINHA II": "COLONINHA",
    "COLONINHA CASA MADEIRA V/A": "COLONINHA",
    "COLONINHA/ VOLTA CURTA": "COLONINHA",
    "JARDIM CIBELI": "JARDIM CIBELE",
    "JARDIM IBELE": "JARDIM CIBELE",
    "JARDIMCIBELE": "JARDIM CIBELE",
    "JD DAS AVENIDAS": "JARDIM DAS AVENIDAS",
    "P0LICIA RODOVIARIA": "POLICIA RODOVIARIA",
    "POL.RODOVIARIA": "POLICIA RODOVIARIA",
    "POLICIA RDODOVIARIA": "POLICIA RODOVIARIA",
    "POLICIA ROD": "POLICIA RODOVIARIA",
    "POLICIA ROOVIARIA": "POLICIA RODOVIARIA",
    "URRUSANGUINHA": "URUSSANGUINHA",
    "URUSSAGUINHA": "URUSSANGUINHA",
    "URUSSANGINHA": "URUSSANGUINHA",
    "URUSSANGUIMHA": "URUSSANGUINHA",
    "URUSSANGUINA": "URUSSANGUINHA",
    "SANGA DA TOCA 1": "SANGA DA TOCA 1A",
}

MESES_S2 = ("2025-08", "2025-09", "2025-10", "2025-11", "2025-12")
MESES_S1 = ("2026-01", "2026-02", "2026-03", "2026-04", "2026-05")


@st.cache_data(show_spinner="Preparando dispensação de medicamentos...")
def load_med() -> pd.DataFrame:
    """DataFrame pronto: datas, custo, bairro, apresentação e perfil."""
    df = load_dispensacao().copy()
    df = _datas(df)
    df = _custo_e_nulos(df)
    df = _bairro_e_cc(df)
    df = _apresentacao(df)
    df = _perfis(df)
    return _junta_censo(df)


def periodo_med(df: pd.DataFrame) -> str:
    """Rótulo do período (mês/ano mínimo–máximo)."""
    meses = df["ano_mes"].dropna()
    if meses.empty:
        return "sem período"
    return f"{meses.min()} a {meses.max()}"


def mes_parcial(df: pd.DataFrame) -> str | None:
    """Mês incompleto (ainda em andamento), se houver."""
    marcados = df.loc[df["eh_mes_parcial"], "ano_mes"]
    return None if marcados.empty else str(marcados.iloc[0])


def meses_completos(df: pd.DataFrame) -> pd.DataFrame:
    """Recorte sem o mês parcial (médias, sazonalidade, anomalias)."""
    return df.loc[~df["eh_mes_parcial"]].copy()


def identificar_mes_parcial(df: pd.DataFrame, coluna_data: str = "data") -> pd.Period | None:
    """Último mês incompleto da base, ou None se já fechou."""
    ultima = df[coluna_data].max()
    if pd.isna(ultima):
        return None
    fim_mes = ultima.to_period("M").end_time.normalize()
    if ultima.normalize() < fim_mes:
        return ultima.to_period("M")
    return None


def _datas(df: pd.DataFrame) -> pd.DataFrame:
    """Converte data, deriva ano_mes e marca mês parcial."""
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["ano_mes"] = df["data"].dt.to_period("M").astype(str)
    parcial = identificar_mes_parcial(df)
    df["eh_mes_parcial"] = (
        df["data"].dt.to_period("M") == parcial if parcial is not None else False
    )
    df["semestre"] = df["ano_mes"].map(_semestre)
    return df


def _semestre(mes: str) -> str | None:
    """Classifica o mês em semestre completo ou parcial."""
    if not mes or mes == "NaT":
        return None
    if mes >= "2026-07":
        return "S2/2026 (parcial)"
    if mes >= "2026-01":
        return "S1/2026"
    return "S2/2025"


def _custo_e_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Preenche nulos e calcula custo_total."""
    df["fabricante_nome"] = df["fabricante_nome"].fillna("NÃO INFORMADO")
    df["classe_terapeutica"] = df["classe_terapeutica"].fillna("INSUMO / OUTROS")
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)
    df["custo_medio"] = pd.to_numeric(df["custo_medio"], errors="coerce").fillna(0)
    df["custo_total"] = df["quantidade"] * df["custo_medio"]
    return df


def _apresentacao(df: pd.DataFrame) -> pd.DataFrame:
    """Monta rótulo completo da apresentação (nome + dose + tipo)."""
    base = df["material_nome_base"].fillna("").astype(str)
    compl = df.get("material_descricao_complementar", pd.Series("", index=df.index))
    tipo = df.get("material_tipo", pd.Series("", index=df.index))
    df["apresentacao_completa"] = (
        base + " " + compl.fillna("").astype(str) + " " + tipo.fillna("").astype(str)
    ).str.strip()
    return df


def _perfis(df: pd.DataFrame) -> pd.DataFrame:
    """Classifica cada registro em um perfil de cuidado."""
    nome = df["material_nome"].fillna("").astype(str)
    compl = df.get("material_descricao_complementar", pd.Series("", index=df.index))
    texto = (nome + " " + compl.fillna("").astype(str)).str.strip()
    df["perfil_cuidado"] = texto.map(_classificar_perfil)
    return df


def _classificar_perfil(nome: str) -> str:
    """Primeiro perfil cujo termo aparece no nome normalizado."""
    norm = _ascii_upper(nome)
    if not norm:
        return PERFIL_OUTROS
    for perfil, termos in MAPA_PERFIS.items():
        for termo in termos:
            if termo in norm:
                return perfil
    return PERFIL_OUTROS


def _ascii_upper(texto: str) -> str:
    """Remove acentos e deixa em maiúsculas para match de keywords."""
    limpo = unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("ASCII")
    return limpo.upper()


def _bairro_e_cc(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza bairro e deixa explícito o centro de custo ausente."""
    df["bairro_nome"] = df["bairro_nome"].fillna("").astype(str).str.strip().str.upper()
    df["bairro_nome"] = df["bairro_nome"].map(_sem_acento)
    df["bairro_padronizado"] = df["bairro_nome"].replace(_CORRECAO)
    df["bairro_malformado"] = (
        df["bairro_nome"].str.contains(r"-{3,}", regex=True, na=False)
        | df["bairro_nome"].str.contains(",", regex=False, na=False)
        | df["bairro_nome"].isin(_PLACEHOLDERS)
    )
    df["centro_custo_nome"] = (
        df["centro_custo_nome"].astype(str).str.strip().replace({"nan": None, "None": None})
    )
    df["centro_custo_nome"] = df["centro_custo_nome"].fillna("Sem Centro de Custo")
    return df


def _sem_acento(texto: str) -> str:
    """Remove acentos e símbolos ordinais."""
    limpo = "".join(
        c for c in unicodedata.normalize("NFD", str(texto)) if unicodedata.category(c) != "Mn"
    )
    return limpo.replace("ª", "A").replace("º", "O")


def _junta_censo(df: pd.DataFrame) -> pd.DataFrame:
    """Associa população do Censo 2022 pela chave normalizada."""
    caminho = csv_censo_bairros()
    if not caminho.exists():
        df["populacao_bairro"] = pd.NA
        df["no_censo"] = False
        return df
    censo = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
    mapa = dict(zip(censo["chave_normalizada"], censo["populacao_censo_2022"]))
    chave = df["bairro_padronizado"].str.replace(r"\(.*?\)", "", regex=True).str.strip()
    df["chave_censo"] = chave
    df["populacao_bairro"] = chave.map(mapa)
    df["no_censo"] = df["populacao_bairro"].notna()
    return df
