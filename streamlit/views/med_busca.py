"""Busca de medicamento e lugares no último mês."""

import streamlit as st

from charts import med_busca as graficos
from components.plot import plot_or_caption
from components.voltar import faixa_titulo
from data.med_busca import nomes_medicamentos, recorte_mes, tabela_lugares, ultimo_mes
from data.prepare_med import load_med
from views.common import exige


def render() -> None:
    """Página de busca: medicamento → lugares do último mês."""
    df = exige(load_med, "Nenhuma dispensação encontrada.")
    mes = ultimo_mes(df)
    faixa_titulo("", "medicamentos")
    escolha = _busca(df, mes)
    if escolha:
        _resultado(df, escolha, mes)


def _busca(df, mes: str):
    """Título + combobox no mesmo visual da busca do header."""
    chave = "med_busca_barra" if st.session_state.get("med_busca_q") else "med_busca_hero"
    with st.container(key=chave):
        _, meio, _ = st.columns([0.8, 2.4, 0.8])
        with meio:
            return _combobox(df, mes)


def _combobox(df, mes: str):
    """Campo de busca igual ao de datasets do topo."""
    st.html(
        '<p class="med-busca-logo">Buscar medicamento</p>'
        f'<p class="med-busca-periodo">Último mês · {mes}</p>'
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


def _resultado(df, nome: str, mes: str) -> None:
    """Lugares do último mês e gráfico quantidade."""
    tabela = tabela_lugares(recorte_mes(df, nome, mes))
    st.markdown(f"### {nome}")
    st.caption(f"Lugares com dispensação em {mes}")
    if tabela.empty:
        st.info("Não houve dispensação deste medicamento no último mês.")
        return
    st.dataframe(tabela, hide_index=True, width="stretch")
    plot_or_caption(*graficos.quantidade_por_lugar(tabela, nome, mes))
