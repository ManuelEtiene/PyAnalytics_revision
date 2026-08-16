"""Menu lateral em drawer fixo na tela (não no fluxo da página)."""

import streamlit as st

from catalog import TOPICS
from navigation import page


def render_drawer() -> None:
    """Painel esquerdo, só enquanto o hambúrguer estiver aberto."""
    if not st.session_state.get("menu_aberto"):
        return
    with st.container(key="pya_drawer", border=False):
        render_menu_links()


def render_menu_links() -> None:
    """Seções Geral e Datasets, com SIM recolhível."""
    _secao_geral()
    _secao_datasets()


def _secao_geral() -> None:
    """Início e Sobre o projeto."""
    st.markdown("**Geral**")
    _item("home", "Início", ":material/dashboard:")
    _item("sobre", "Sobre PyAnalytics", ":material/info:")


def _secao_datasets() -> None:
    """Pasta SIM; a seta abre os subtópicos."""
    st.markdown("**Datasets**")
    with st.expander("SIM (Mortalidade)", expanded=False):
        _item("sim", "Visão da base", ":material/folder_open:")
        for topico in TOPICS:
            sufixo = "" if topico.ready else " · em breve"
            _item(topico.id, f"{topico.title}{sufixo}", f":material/{topico.icon}:")


def _item(page_id: str, label: str, icon: str) -> None:
    """Um atalho do menu."""
    st.page_link(page(page_id), label=label, icon=icon)
