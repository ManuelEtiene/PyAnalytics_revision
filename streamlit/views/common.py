"""Carrega o Retrato ou interrompe a página com erro amigável."""

import streamlit as st

from data.prepare_retrato import load_retrato, periodo_titulo


def load_or_stop():
    """Devolve o DataFrame preparado; para a página se o CSV não existir."""
    try:
        df = load_retrato()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    if df.empty:
        st.warning("Nenhum óbito de Araranguá encontrado no CSV.")
        st.stop()
    return df


def periodo(df) -> str:
    """Atalho para o rótulo do período."""
    return periodo_titulo(df)
