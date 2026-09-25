"""Hub da base Medicamentos: análises, problema, fonte e links."""

import streamlit as st

from catalog import TOPICS_MED
from components.carousel import html_analises
from components.voltar import faixa_titulo
from views.med_bairro import render as render_bairro
from views.med_busca import render as render_busca
from views.med_custos import render as render_custos
from views.med_destaques import render as render_destaques
from views.med_perfis import render as render_perfis
from views.med_tempo import render as render_tempo

_TEMAS = {
    "busca": render_busca,
    "tempo": render_tempo,
    "destaques": render_destaques,
    "bairro-cc": render_bairro,
    "perfis": render_perfis,
    "custos": render_custos,
}


def render() -> None:
    """Visão geral (/medicamentos) ou um tema (/medicamentos?tema=custos)."""
    tema = st.query_params.get("tema", "")
    destino = _TEMAS.get(tema)
    if callable(destino):
        destino()
        return
    _visao_geral()


def _visao_geral() -> None:
    """Página central da base de medicamentos."""
    with st.container(key="hub_base"):
        faixa_titulo("Medicamentos — Dispensação pública", "home")
        st.html(html_analises(TOPICS_MED))
        st.markdown("## Sobre a base")
        st.markdown(
            "### O problema\n"
            "Entender **o que se dispensa, quanto custa e onde** ajuda a gestão da "
            "farmácia pública a priorizar estoque, orçamento e acesso nos bairros."
        )
        st.markdown(
            "### A base\n"
            "Registros de **dispensação da Farmácia Básica Municipal de Araranguá**, "
            "com medicamento, bairro, centro de custo, quantidade e custo médio."
        )
