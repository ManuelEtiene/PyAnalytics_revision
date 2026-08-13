"""Página inicial: KPIs, atalhos e preview da série histórica."""

import streamlit as st

from catalog import TOPICS
from charts.perfil import obitos_por_ano
from components.cards import alert_card, kpi_card, topic_card
from components.plot import plot
from data.kpis import resumo_home
from navigation import page
from views.common import load_or_stop, periodo

DESTAQUES = ("retrato", "onde_morrem", "violentas")


def render() -> None:
    """Monta a Home com dados reais do Retrato."""
    df = load_or_stop()
    kpis = resumo_home(df)
    _kpis(kpis)
    st.write("")
    _alerta(kpis)
    st.write("")
    _atalhos()
    st.write("")
    _preview(df, periodo(df))


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
    """Card da causa principal, com atalho para o Retrato."""
    st.markdown(
        alert_card(
            "Causa mais frequente",
            kpis["causa"],
            "Principal causa básica de óbito entre residentes de Araranguá.",
            _br(kpis["n_causa"]),
            f"{kpis['pct_causa']:.1f}% do total no período",
        ),
        unsafe_allow_html=True,
    )
    st.page_link(page("retrato"), label="Ver retrato da mortalidade", icon=":material/analytics:")


def _atalhos() -> None:
    """Três cards clicáveis para tópicos da SIM."""
    st.markdown('<p class="section-title">Explore os temas</p>', unsafe_allow_html=True)
    colunas = st.columns(3)
    por_id = {item.id: item for item in TOPICS}
    for coluna, item_id in zip(colunas, DESTAQUES):
        item = por_id[item_id]
        status = "Disponível" if item.ready else "Em breve"
        with coluna:
            st.markdown(
                topic_card("SIM", item.short, item.description, status),
                unsafe_allow_html=True,
            )
            st.page_link(page(item.id), label="Abrir", icon=f":material/{item.icon}:")


def _preview(df, periodo_txt: str) -> None:
    """Gráfico de óbitos por ano levando ao Retrato."""
    st.markdown('<p class="section-title">Visão geral da mortalidade</p>', unsafe_allow_html=True)
    fig, insight = obitos_por_ano(df, periodo_txt)
    plot(fig, insight)
    st.page_link(page("retrato"), label="Ver todos os gráficos", icon=":material/show_chart:")


def _br(numero: int) -> str:
    """Inteiro no formato brasileiro (15.608)."""
    return f"{numero:,}".replace(",", ".")
