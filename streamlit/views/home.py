"""Página inicial: KPIs e atalhos para as bases do portal."""

import streamlit as st

from catalog import NavItem, bases
from components.cards import alert_card, base_card, kpi_card
from data.kpis import resumo_home
from navigation import link_pagina
from views.common import load_or_stop


def render() -> None:
    """Monta a Home com dados reais do Retrato."""
    df = load_or_stop()
    kpis = resumo_home(df)
    _kpis(kpis)
    st.write("")
    _alerta(kpis)
    st.write("")
    _atalhos()


def _kpis(kpis: dict) -> None:
    """Dois cards grandes: total de óbitos e % hospital."""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(_card_total(kpis), unsafe_allow_html=True)
    with col2:
        st.markdown(_card_hospital(kpis), unsafe_allow_html=True)


def _card_total(kpis: dict) -> str:
    """Card do total de óbitos no período."""
    return kpi_card(
        "Óbitos de residentes",
        _br(kpis["total"]),
        f"Araranguá · {kpis['periodo']}",
        "Série histórica",
        "chip-yellow",
    )


def _card_hospital(kpis: dict) -> str:
    """Card do percentual de óbitos em hospital."""
    return kpi_card(
        "Óbitos em hospital",
        f"{kpis['pct_hospital']:.0f}%",
        "local de ocorrência",
        "SIM",
        "chip-gray",
    )


def _alerta(kpis: dict) -> None:
    """Card da causa principal, com atalho para a Visão da Base."""
    with st.container(key="alerta_causa"):
        st.markdown(_html_alerta(kpis), unsafe_allow_html=True)
        _botao_acessar_dataset()


def _html_alerta(kpis: dict) -> str:
    """HTML do card de causa mais frequente."""
    return alert_card(
        "Causa mais frequente",
        kpis["causa"],
        "Principal causa básica de óbito entre residentes de Araranguá.",
        _br(kpis["n_causa"]),
        f"{kpis['pct_causa']:.1f}% do total no período",
    )


def _botao_acessar_dataset() -> None:
    """Abre a Visão da Base SIM na mesma guia."""
    with st.container(key="alerta_causa_acoes"):
        link_pagina("sim", "Acessar dataset")


def _atalhos() -> None:
    """Cards quadrados: uma base cada (clique vai à visão geral)."""
    st.markdown('<p class="section-title">Explore as bases</p>', unsafe_allow_html=True)
    with st.container(key="explore_bases"):
        colunas = st.columns(len(bases()))
        for coluna, item in zip(colunas, bases()):
            with coluna:
                _card_base(item)


def _card_base(item: NavItem) -> None:
    """Card da base; clique na disponível abre a visão geral."""
    status = "Disponível" if item.ready else "Em breve"
    with st.container(key=f"base_{item.id}"):
        st.html(base_card(item.short, item.description, status))
        if item.ready:
            _abrir_base(item.id)


def _abrir_base(page_id: str) -> None:
    """Mesmo st.page_link de Acessar dataset, cobrindo o card."""
    link_pagina(page_id, "Abrir")


def _br(numero: int) -> str:
    """Inteiro no formato brasileiro (15.608)."""
    return f"{numero:,}".replace(",", ".")
