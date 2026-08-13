"""Páginas-esqueleto dos tópicos da SIM ainda sem gráficos."""

import streamlit as st

from catalog import get_item
from navigation import page


def _render(topic_id: str) -> None:
    """Hub curto: o que será analisado e atalho de volta à SIM."""
    item = get_item(topic_id)
    st.markdown(f"## {item.title}")
    st.info("Esta análise estará disponível em breve.")
    st.markdown(item.description)
    st.page_link(page("sim"), label="Voltar à base SIM", icon=":material/folder_open:")
    st.page_link(page("home"), label="Início", icon=":material/dashboard:")


def pagina_evitavel() -> None:
    """Placeholder: mortalidade evitável."""
    _render("evitavel")


def pagina_materna() -> None:
    """Placeholder: saúde materna e infantil."""
    _render("materna")


def pagina_onde_morrem() -> None:
    """Placeholder: local de ocorrência."""
    _render("onde_morrem")


def pagina_violentas() -> None:
    """Placeholder: mortes violentas."""
    _render("violentas")
