"""Carrega dados do SIM ou interrompe a página com erro amigável."""

import streamlit as st

from data.prepare_sim_retrato import load_retrato, periodo_titulo


def load_or_stop():
    """Devolve o DataFrame do Retrato; para a página se o CSV não existir."""
    return exige(load_retrato, "Nenhum óbito de Araranguá encontrado no CSV.")


def exige(loader, vazio_msg: str):
    """Executa o loader e interrompe se faltar arquivo ou vier vazio."""
    try:
        dados = loader()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    if _vazio(dados):
        st.warning(vazio_msg)
        st.stop()
    return dados


def _vazio(dados) -> bool:
    """True se o retorno não tiver linhas."""
    if dados is None:
        return True
    if hasattr(dados, "empty"):
        return bool(dados.empty)
    if isinstance(dados, tuple):
        return all(hasattr(p, "empty") and p.empty for p in dados)
    return False


def periodo(df) -> str:
    """Atalho para o rótulo do período."""
    return periodo_titulo(df)
