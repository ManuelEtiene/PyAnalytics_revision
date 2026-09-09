"""Página inicial: KPIs e atalhos para as bases do portal."""

import streamlit as st

from catalog import NavItem, bases
from components.cards import alert_card, base_card, kpi_card
from data.kpis import resumo_home
from data.kpis_med import resumo_home_med
from data.paths import csv_dispensacao
from navigation import link_pagina
from views.common import load_or_stop


def render() -> None:
    """Monta a Home com destaques da SIM e de Medicamentos."""
    kpis = resumo_home(load_or_stop())
    kpis_med = _kpis_med_seguros()
    _kpis_sim(kpis)
    st.write("")
    _alerta_sim(kpis)
    if kpis_med:
        st.write("")
        _kpis_med(kpis_med)
        st.write("")
        _alerta_med(kpis_med)
    st.write("")
    _atalhos()


def _kpis_med_seguros() -> dict | None:
    """Carrega KPIs de medicamentos; None se o CSV ainda não existir."""
    try:
        if not csv_dispensacao().exists():
            return None
        from data.prepare_med import load_med

        df = load_med()
        if df is None or getattr(df, "empty", True):
            return None
        return resumo_home_med(df)
    except Exception:
        return None


def _kpis_sim(kpis: dict) -> None:
    """Dois cards grandes: total de óbitos e % hospital."""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(_card_total_sim(kpis), unsafe_allow_html=True)
    with col2:
        st.markdown(_card_hospital(kpis), unsafe_allow_html=True)


def _card_total_sim(kpis: dict) -> str:
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


def _alerta_sim(kpis: dict) -> None:
    """Card da causa principal, com atalho para a Visão da Base."""
    with st.container(key="alerta_causa"):
        st.markdown(_html_alerta_sim(kpis), unsafe_allow_html=True)
        _botao_dataset("sim", "alerta_causa_acoes")


def _html_alerta_sim(kpis: dict) -> str:
    """HTML do card de causa mais frequente."""
    return alert_card(
        "Causa mais frequente",
        kpis["causa"],
        "Principal causa básica de óbito entre residentes de Araranguá.",
        _br(kpis["n_causa"]),
        f"{kpis['pct_causa']:.1f}% do total no período",
    )


def _kpis_med(kpis: dict) -> None:
    """Cards de volume e custo da farmácia básica (clique abre Medicamentos)."""
    col1, col2 = st.columns(2)
    with col1:
        with st.container(key="kpi_med_registros"):
            st.markdown(_card_registros_med(kpis), unsafe_allow_html=True)
            _botao_dataset("medicamentos", "kpi_med_registros_acoes")
    with col2:
        with st.container(key="kpi_med_custo"):
            st.markdown(_card_custo_med(kpis), unsafe_allow_html=True)
            _botao_dataset("medicamentos", "kpi_med_custo_acoes")


def _card_registros_med(kpis: dict) -> str:
    """Card do volume de dispensações."""
    return kpi_card(
        "Dispensações registradas",
        _br(kpis["total"]),
        f"Farmácia Básica · {kpis['periodo']}",
        f"{_br(kpis['medicamentos'])} itens",
        "chip-yellow",
    )


def _card_custo_med(kpis: dict) -> str:
    """Card do custo total estimado."""
    return kpi_card(
        "Custo total estimado",
        _reais(kpis["custo_total"]),
        "quantidade × custo médio",
        "Medicamentos",
        "chip-gray",
    )


def _alerta_med(kpis: dict) -> None:
    """Destaque do medicamento que mais pesa no custo."""
    with st.container(key="alerta_med"):
        st.markdown(_html_alerta_med(kpis), unsafe_allow_html=True)
        _botao_dataset("medicamentos", "alerta_med_acoes")


def _html_alerta_med(kpis: dict) -> str:
    """HTML do card do medicamento de maior custo."""
    return alert_card(
        "Medicamento de maior custo",
        kpis["top_med"],
        "Item que mais concentra o gasto estimado na dispensação pública.",
        _reais(kpis["top_custo"]),
        f"{kpis['top_pct']:.1f}% do custo total no período",
    )


def _botao_dataset(page_id: str, key: str) -> None:
    """PageLink invisível que cobre o card e abre a base."""
    with st.container(key=key):
        link_pagina(page_id, "Acessar dataset")


def _atalhos() -> None:
    """Cards quadrados: uma base cada (clique vai à visão geral)."""
    st.markdown('<p class="section-title">Explore as bases</p>', unsafe_allow_html=True)
    with st.container(key="explore_bases"):
        colunas = st.columns(len(bases()))
        for coluna, item in zip(colunas, bases()):
            with coluna:
                _card_base(item)


def _card_base(item: NavItem) -> None:
    """Card da base; clique abre a visão geral (mesmo se ainda em breve)."""
    status = "Disponível" if item.ready else "Em breve"
    with st.container(key=f"base_{item.id}"):
        st.html(base_card(item.short, item.description, status, item.ready))
        link_pagina(item.id, "Abrir")


def _br(numero: int) -> str:
    """Inteiro no formato brasileiro (15.608)."""
    return f"{numero:,}".replace(",", ".")


def _reais(valor: float) -> str:
    """Valor em R$ abreviado (R$ 2,2 mi)."""
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.1f} mi".replace(".", ",")
    if valor >= 1_000:
        return f"R$ {valor / 1_000:.0f} mil"
    return f"R$ {valor:,.0f}".replace(",", ".")
