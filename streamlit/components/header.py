"""Header fixo: título, busca e hambúrguer que abre o drawer."""

import base64
from pathlib import Path

import streamlit as st

from catalog import all_items
from navigation import page

# Preferência: assets/ do repositório; fallback: streamlit/assets/
_REPO_LOGO = Path(__file__).resolve().parents[2] / "assets" / "IconPyAnalytics.png"
_LOCAL_LOGO = Path(__file__).resolve().parents[1] / "assets" / "pyanalytics.png"
LOGO = _REPO_LOGO if _REPO_LOGO.exists() else _LOCAL_LOGO


def render_header() -> None:
    """Faixa do topo (CSS deixa fixa na tela)."""
    nav, marca, busca, icones = st.columns(
        [1.0, 3.2, 4.5, 0.55], vertical_alignment="center"
    )
    with nav:
        _botoes_nav()
    with marca:
        _marca()
    with busca:
        _busca_combobox()
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
        st.switch_page(page(por_titulo[escolha].id))


def _botao_tema() -> None:
    """Alterna entre tema claro e escuro."""
    escuro = st.session_state.get("tema_escuro", False)
    icone = ":material/light_mode:" if escuro else ":material/dark_mode:"
    with st.container(key="tema_modo"):
        if st.button(
            "Tema",
            key="btn_tema",
            icon=icone,
            type="tertiary",
        ):
            st.session_state.tema_escuro = not escuro
            st.rerun()


def _botoes_nav() -> None:
    """Hambúrguer, info e início na mesma faixa, bem juntos."""
    with st.container(key="header_nav"):
        menu, sobre, inicio = st.columns(3, gap="small")
        with menu:
            _botao_menu()
        with sobre:
            with st.container(key="header_sobre"):
                st.page_link(page("sobre"), label="Sobre", icon=":material/info:")
        with inicio:
            with st.container(key="header_home"):
                st.page_link(page("home"), label="Início", icon=":material/home:")


def _marca() -> None:
    """Logo e nome do PyAnalytics (sem fullscreen ao clicar)."""
    imagem = base64.b64encode(LOGO.read_bytes()).decode()
    with st.container(key="pya_brand"):
        st.html(
            f"""
            <div class="pya-brand-row">
              <img class="pya-logo" src="data:image/png;base64,{imagem}"
                   alt="PyAnalytics" width="200" height="200">
              <span class="pya-title">PyAnalytics</span>
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
