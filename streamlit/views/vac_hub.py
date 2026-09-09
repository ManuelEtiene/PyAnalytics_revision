"""Hub da base Vacinações: análises e contexto."""

import streamlit as st

from catalog import TOPICS_VAC, get_item
from components.carousel import html_analises
from components.voltar import faixa_titulo
from views.sim_tema import cabecalho


# Temas: /vacinas?tema=<slug>
_TEMAS = {
    "tempo": "vac_tempo",
    "destaques": "vac_destaques",
    "salas-bairros": "vac_salas",
    "estrategias": "vac_estrategias",
    "doses": "vac_doses",
    "origem": "vac_origem",
    "lotes": "vac_lotes",
}


def render() -> None:
    """Visão geral (/vacinas) ou um tema (/vacinas?tema=tempo)."""
    tema = st.query_params.get("tema", "")
    item_id = _TEMAS.get(tema)
    if item_id:
        _placeholder(item_id)
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
            "Ver **quando, onde e como** as vacinas foram aplicadas ajuda a cidade a "
            "acompanhar o serviço sem confundir aplicação com cobertura da população."
        )
        st.markdown(
            "### A base\n"
            "Aplicações de vacinas em **Araranguá (jan–jun/2026)**: cerca de "
            "**31 mil** registros em **15 salas**, com vacina, dose, estratégia, "
            "origem do registro, lote e validade. Pacientes estão anonimizados."
        )


def _placeholder(item_id: str) -> None:
    """Tema ainda sem gráficos — mostra a pergunta-guia."""
    item = get_item(item_id)
    cabecalho(item.title, "Araranguá · jan–jun/2026 · em preparação", "vacinas")
    st.info("Análise em preparação. Em breve os gráficos desta pergunta.")
    st.markdown(f"**Pergunta-guia:** {item.description}")
