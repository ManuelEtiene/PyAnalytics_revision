"""Menu lateral em drawer fixo na tela (não no fluxo da página)."""

import streamlit as st

from catalog import TOPICS_MED, TOPICS_SIM, VACINAS
from navigation import link_pagina


def render_drawer() -> None:
    """Painel esquerdo, só enquanto o hambúrguer estiver aberto."""
    if not st.session_state.get("menu_aberto"):
        return
    with st.container(key="pya_drawer", border=False):
        render_menu_links()


def render_menu_links() -> None:
    """Seções Geral e Datasets."""
    _secao_geral()
    _secao_datasets()


def _secao_geral() -> None:
    """Início e Sobre o projeto."""
    st.markdown("**Geral**")
    _item("home", "Início", ":material/dashboard:")
    _item("sobre", "Sobre PyAnalytics", ":material/info:")


def _secao_datasets() -> None:
    """Pastas das bases; Vacinações fica apagada até a base existir."""
    st.markdown("**Datasets**")
    _pasta("SIM (Mortalidade)", "sim", TOPICS_SIM, "folder_open")
    _pasta("Medicamentos", "medicamentos", TOPICS_MED, "medication")
    _pasta_em_breve(VACINAS.short)


def _pasta(titulo: str, hub_id: str, topicos, icone: str) -> None:
    """Expander com visão da base e subtópicos."""
    with st.expander(titulo, expanded=False):
        _item(hub_id, "Visão da base", f":material/{icone}:")
        for topico in topicos:
            _item(topico.id, _rotulo(topico), f":material/{topico.icon}:")


def _rotulo(topico) -> str:
    """Busca usa o nome curto; análises ficam com o título completo."""
    return topico.short if topico.id == "med_busca" else topico.title


def _pasta_em_breve(titulo: str) -> None:
    """Base ainda sem conteúdo: apagada e sem navegação."""
    with st.container(key="dataset_desabilitado"):
        with st.expander(titulo, expanded=False):
            pass


def _item(page_id: str, label: str, icon: str) -> None:
    """Um atalho do menu."""
    link_pagina(page_id, label, icon)
