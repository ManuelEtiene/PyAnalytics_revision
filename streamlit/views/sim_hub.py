"""Hub da base SIM: análises, problema, fonte e links."""

import streamlit as st

from catalog import TOPICS
from components.carousel import html_analises
from components.voltar import faixa_titulo
from views.sim_evitavel import render as render_evitavel
from views.sim_local import render as render_local
from views.sim_materna import render as render_materna
from views.sim_retrato import render as render_retrato
from views.sim_violentas import render as render_violentas

API_SIM = (
    "https://apidadosabertos.saude.gov.br/vigilancia-e-meio-ambiente/"
    "sistema-de-informacao-sobre-mortalidade"
)
DOC_SIM = "https://datasus.saude.gov.br/mortalidade-desde-1996-pela-cid-10"


# Temas da SIM: /sim?tema=<slug> (Streamlit não aceita /sim/retrato).
_TEMAS = {
    "retrato": render_retrato,
    "evitavel": render_evitavel,
    "onde-morrem": render_local,
    "violentas": render_violentas,
    "materna": render_materna,
}


def render() -> None:
    """Visão geral (/sim) ou um tema (/sim?tema=retrato)."""
    visao = _TEMAS.get(st.query_params.get("tema", ""))
    if visao:
        visao()
        return
    _visao_geral()


def _visao_geral() -> None:
    """Página central da SIM, de onde saem os temas."""
    faixa_titulo("SIM — Sistema de Informações sobre Mortalidade", "home")
    _grade()
    _sobre_a_base()


def _grade() -> None:
    """Cards iguais: 3 na primeira linha, 2 na segunda."""
    st.html(html_analises(TOPICS))


def _sobre_a_base() -> None:
    """Contexto da SIM: problema, recorte e fontes."""
    st.markdown("## Sobre a base")
    _problema()
    _base()
    _links()


def _problema() -> None:
    """Por que olhar mortalidade em Araranguá."""
    st.markdown("### O problema")
    st.markdown(
        "Saber **quem morre, de quê, onde e com qual perfil** ajuda a cidade a "
        "enxergar desigualdades, causas evitáveis e a rede de cuidado. Sem um "
        "painel público, esses números ficam presos em planilhas do DATASUS."
    )


def _base() -> None:
    """O que é a SIM e o recorte usado."""
    st.markdown("### A base")
    st.markdown(
        "A **SIM** registra as Declarações de Óbito no Brasil. Neste portal "
        "usamos o recorte de **residentes de Araranguá (SC)**, com colunas já "
        "tratadas pelo pipeline do PyAnalytics (sexo, raça/cor, local, idade, causa)."
    )


def _links() -> None:
    """Fontes oficiais para quem quiser ir além do painel."""
    st.markdown("### Links")
    st.markdown(f"- [API de Dados Abertos — SIM]({API_SIM})")
    st.markdown(f"- [Documentação DATASUS (CID-10)]({DOC_SIM})")
