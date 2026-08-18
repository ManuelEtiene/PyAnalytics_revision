"""Menu lateral em drawer fixo na tela (não no fluxo da página)."""

import streamlit as st

from catalog import TOPICS
from navigation import link_pagina


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
    """Pastas das bases; Medicamentos ainda não é navegável."""
    st.markdown("**Datasets**")
    _pasta_sim()
    _item_desabilitado("Medicamentos")


def _pasta_sim() -> None:
    """SIM com visão da base e subtópicos."""
    with st.expander("SIM (Mortalidade)", expanded=False):
        _item("sim", "Visão da base", ":material/folder_open:")
        for topico in TOPICS:
            _item(topico.id, topico.title, f":material/{topico.icon}:")


def _item(page_id: str, label: str, icon: str) -> None:
    """Um atalho do menu (temas SIM abrem /sim?tema=)."""
    link_pagina(page_id, label, icon)


def _item_desabilitado(label: str) -> None:
    """Mesmo visual do expander SIM, sem abrir nem navegar."""
    with st.container(key="dataset_desabilitado"):
        with st.expander(f"{label} (em breve)", expanded=False):
            pass
