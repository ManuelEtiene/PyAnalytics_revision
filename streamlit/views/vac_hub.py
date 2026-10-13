"""Hub da base Vacinações: análises, problema, fonte e links."""

import streamlit as st

from catalog import TOPICS_VAC
from components.carousel import html_analises
from components.voltar import faixa_titulo
from views.vac_bairros import render as render_bairros
from views.vac_destaques import render as render_destaques
from views.vac_doses import render as render_doses
from views.vac_estrategias import render as render_estrategias
from views.vac_lotes import render as render_lotes
from views.vac_origem import render as render_origem
from views.vac_tempo import render as render_tempo

_TEMAS = {
    "tempo": render_tempo,
    "destaques": render_destaques,
    "bairros": render_bairros,
    "salas-bairros": render_bairros,  # URL antiga
    "estrategias": render_estrategias,
    "doses": render_doses,
    "origem": render_origem,
    "lotes": render_lotes,
}


def render() -> None:
    """Visão geral (/vacinas) ou um tema (/vacinas?tema=tempo)."""
    tema = st.query_params.get("tema", "")
    destino = _TEMAS.get(tema)
    if callable(destino):
        destino()
        return
    _visao_geral()


def _visao_geral() -> None:
    """Página central da base de vacinações."""
    with st.container(key="hub_base"):
        faixa_titulo("Vacinações — Araranguá", "home")
        st.html(html_analises(TOPICS_VAC))
        st.markdown("## Sobre a base")
        st.markdown(
            "### O problema\n"
            "Ver **quando, onde (bairro da pessoa) e como** as vacinas foram aplicadas "
            "ajuda a cidade a acompanhar o serviço sem confundir aplicação com cobertura "
            "da população."
        )
        st.markdown(
            "### A base\n"
            "Aplicações de vacinas em **Araranguá (fev–jun/2026)**: cerca de "
            "**31 mil** registros em **15 bairros**, com vacina, dose, estratégia, "
            "origem do registro, lote e validade. O bairro é o da pessoa vacinada — "
            "não a unidade de aplicação. Pacientes estão anonimizados."
        )
