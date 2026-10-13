"""Prepara a base de vacinas para os temas da Sprint 3."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from data.load_vacinas import load_vacinas
from data.vac_nomes import nome_vacina_curto

_ESTRATEGIA = {
    "Rotina (1)": "Rotina",
    "Pós": "Pós-exposição",
    "Monitoramento das Estratégias de Vacinação": "Monitoramento",
}


@st.cache_data(show_spinner="Preparando vacinações...")
def load_vac() -> pd.DataFrame:
    """DataFrame pronto: datas, bairro da pessoa, estratégia e dose agrupada."""
    df = load_vacinas().copy()
    df = _textos(df)
    df = _datas(df)
    df = _lotes(df)
    return df


def periodo_vac(df: pd.DataFrame) -> str:
    """Rótulo do período com data válida (mês/ano)."""
    meses = df["mes_label"].dropna()
    if meses.empty:
        return "sem período"
    ordem = df.loc[df["mes_label"].notna()].sort_values("data_aplicacao")
    return f"{ordem['mes_label'].iloc[0]} a {ordem['mes_label'].iloc[-1]}"


def _textos(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza textos e cria bairro / flags."""
    for col in ("nome_do_bairro", "nome_da_vacina", "estrategia", "dose", "origem", "lote"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
    df["estrategia"] = df["estrategia"].replace(_ESTRATEGIA)
    # Bairro da pessoa vacinada (não é local de aplicação)
    df["bairro"] = df["nome_do_bairro"].fillna("Não informado")
    df["origem"] = df["origem"].fillna("Não informado")
    df["dose"] = df["dose"].fillna("Não informado")
    df["eh_influenza"] = df["nome_da_vacina"].str.contains("influ", case=False, na=False)
    df["vacina_curta"] = df["nome_da_vacina"].map(nome_vacina_curto)
    df["dose_grupo"] = df["dose"].map(_grupo_dose)
    return df


def _datas(df: pd.DataFrame) -> pd.DataFrame:
    """Converte datas e cria rótulos mês/dia rastreáveis."""
    df["data_aplicacao_bruta"] = df["data_da_aplicacao"]
    df["data_aplicacao"] = pd.to_datetime(
        df["data_da_aplicacao"], dayfirst=True, errors="coerce"
    )
    df["mes_periodo"] = df["data_aplicacao"].dt.to_period("M")
    df["mes_label"] = df["data_aplicacao"].dt.strftime("%m/%Y")
    df["dia_label"] = df["data_aplicacao"].dt.strftime("%d/%m/%Y")
    df["ano_mes"] = df["data_aplicacao"].dt.strftime("%Y-%m")
    return df


def _lotes(df: pd.DataFrame) -> pd.DataFrame:
    """Validade do lote e prazo restante em dias na aplicação."""
    df["validade_lote"] = pd.to_datetime(
        df["validade_do_lote"], dayfirst=True, errors="coerce"
    )
    df["prazo_restante_dias"] = (df["validade_lote"] - df["data_aplicacao"]).dt.days
    return df


def _grupo_dose(texto) -> str:
    """Agrupa textos parecidos de dose em categorias simples."""
    if texto is None or (isinstance(texto, float) and np.isnan(texto)):
        return "Não informado"
    t = str(texto).upper()
    if "ÚNICA" in t or "UNICA" in t:
        return "Única"
    if "REFOR" in t:
        return "Reforço"
    if "1" in t and "DOSE" in t:
        return "1ª dose"
    if "2" in t and "DOSE" in t:
        return "2ª dose"
    if "3" in t and "DOSE" in t:
        return "3ª dose"
    if "4" in t and "DOSE" in t:
        return "4ª dose"
    if t.strip() == "DOSE":
        return "Dose (sem ordem)"
    return "Outras"
