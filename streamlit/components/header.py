"""Header fixo: título, busca e hambúrguer que abre o drawer."""

import base64
from pathlib import Path

import streamlit as st

from catalog import all_items
from components.tema import ativo, alternar
from navigation import abrir, href, link_pagina

# Preferência: assets/ do repositório; fallback: streamlit/assets/
_REPO_LOGO = Path(__file__).resolve().parents[2] / "assets" / "IconPyAnalytics.png"
_LOCAL_LOGO = Path(__file__).resolve().parents[1] / "assets" / "pyanalytics.png"
LOGO = _REPO_LOGO if _REPO_LOGO.exists() else _LOCAL_LOGO


def render_header() -> None:
    """Faixa do topo (CSS deixa fixa na tela)."""
    aberto = st.session_state.get("busca_aberta", False)
    marcador = "busca_aberta" if aberto else "busca_fechada"
    with st.container(key=marcador):
        nav, marca, busca, lupa, icones = st.columns(
            [1.0, 3.2, 4.5, 0.55, 0.55], vertical_alignment="center"
        )
        with nav:
            _botoes_nav()
        with marca:
            _marca()
        with busca:
            _busca_combobox()
        with lupa:
            _botao_busca()
        with icones:
            _botao_tema()


def _busca_combobox() -> None:
    """Combobox: digita para filtrar e seleciona a página."""
    itens = all_items()
    por_titulo = {item.title: item for item in itens}
    escolha = st.selectbox(
        "Buscar",
        options=list(por_titulo),
        index=None,
        placeholder="Buscar datasets...",
        label_visibility="collapsed",
        key="nav_search",
        filter_mode="fuzzy",
    )
    ultima = st.session_state.get("_busca_aplicada")
    if escolha and escolha != ultima and escolha in por_titulo:
        st.session_state._busca_aplicada = escolha
        abrir(por_titulo[escolha].id)


def _botao_busca() -> None:
    """Abre ou fecha a barra de pesquisa no mobile."""
    aberto = st.session_state.get("busca_aberta", False)
    with st.container(key="btn_busca"):
        if st.button(
            "Buscar",
            key="btn_lupa",
            icon=":material/search:",
            type="tertiary",
        ):
            st.session_state.busca_aberta = not aberto
            st.rerun()


def _botao_tema() -> None:
    """Alterna entre tema claro e escuro."""
    icone = ":material/light_mode:" if ativo() else ":material/dark_mode:"
    with st.container(key="tema_modo"):
        if st.button(
            "Tema",
            key="btn_tema",
            icon=icone,
            type="tertiary",
        ):
            alternar()


def _botoes_nav() -> None:
    """Hambúrguer e início na mesma faixa."""
    with st.container(key="header_nav"):
        menu, inicio = st.columns(2, gap="small")
        with menu:
            _botao_menu()
        with inicio:
            with st.container(key="header_home"):
                link_pagina("home", "Início", ":material/home:")


def _marca() -> None:
    """Logo e título no mesmo lugar de antes; o nome abre Sobre."""
    imagem = base64.b64encode(LOGO.read_bytes()).decode()
    with st.container(key="pya_brand"):
        st.html(
            f"""
            <div class="pya-brand-row">
              <img class="pya-logo" src="data:image/png;base64,{imagem}"
                   alt="PyAnalytics" width="200" height="200">
              <a class="pya-title" href="{href('sobre')}" target="_self">PyAnalytics</a>
            </div>
            """
        )


def _botao_menu() -> None:
    """Abre ou fecha o menu lateral fixo na tela."""
    if st.button(
        "Menu",
        key="abrir_menu",
        icon=":material/menu:",
        type="tertiary",
    ):
        st.session_state.menu_aberto = not st.session_state.get("menu_aberto", False)
