"""Busca REMUME: onde o medicamento é dispensado (unidades/farmácia)."""

import streamlit as st

from components.voltar import faixa_titulo
from data.med_busca import (
    load_busca,
    nomes_medicamentos,
    recorte,
    resumo,
    tabela_apresentacoes,
    tabela_lugares,
    total_itens,
)
from views.common import exige


def render() -> None:
    """Medicamento → apresentações e unidades de dispensação (REMUME)."""
    df = exige(load_busca, "Nenhum medicamento encontrado na REMUME.")
    faixa_titulo("", "medicamentos")
    escolha = _busca(df)
    if escolha:
        _resultado(df, escolha)


def _busca(df):
    """Título + combobox no mesmo visual da busca do header."""
    chave = "med_busca_barra" if st.session_state.get("med_busca_q") else "med_busca_hero"
    with st.container(key=chave):
        _, meio, _ = st.columns([0.8, 2.4, 0.8])
        with meio:
            return _combobox(df)


def _combobox(df):
    """Campo de busca igual ao de datasets do topo."""
    st.html(
        '<p class="med-busca-logo">Buscar medicamento</p>'
        f'<p class="med-busca-periodo">REMUME · {total_itens(df)} itens · locais de dispensação</p>'
    )
    return st.selectbox(
        "Buscar medicamento",
        options=nomes_medicamentos(df),
        index=None,
        placeholder="Buscar medicamento...",
        label_visibility="collapsed",
        key="med_busca_q",
        filter_mode="fuzzy",
    )


def _resultado(df, nome: str) -> None:
    """Apresentações e unidades que dispensam, conforme a REMUME."""
    dados = recorte(df, nome)
    info = resumo(dados)
    st.markdown(f"### {nome}")
    st.markdown(_html_resumo(info), unsafe_allow_html=True)

    apresentacoes = tabela_apresentacoes(dados)
    lugares = tabela_lugares(dados)
    if apresentacoes.empty:
        st.info("Medicamento não encontrado na REMUME.")
        return

    st.markdown("#### Apresentações na REMUME")
    st.dataframe(apresentacoes, hide_index=True, width="stretch")

    st.markdown("#### Unidades que dispensam")
    st.dataframe(lugares, hide_index=True, width="stretch")


def _html_resumo(info: dict) -> str:
    """Três cards no visual do portal (legível no claro e no escuro)."""
    acesso = _texto_acesso(bool(info["tem_farmacia"]), bool(info["tem_ubs"]))
    cards = (
        _card_resumo("Apresentações", str(info["apresentacoes"])),
        _card_resumo("Unidades", str(info["lugares"])),
        _card_resumo("Dispensado em", acesso),
    )
    return '<div class="med-busca-resumo">' + "".join(cards) + "</div>"


def _card_resumo(titulo: str, valor: str) -> str:
    """Card compacto de indicador."""
    return (
        f'<div class="glass-card med-busca-kpi">'
        f'<p class="topic-kicker">{titulo}</p>'
        f'<div class="kpi-value">{valor}</div>'
        f"</div>"
    )


def _texto_acesso(farmacia: bool, ubs: bool) -> str:
    """Rótulo curto do tipo de unidade na REMUME."""
    if farmacia and ubs:
        return "Farmácia + UBS"
    if ubs:
        return "UBS"
    return "Farmácia"
