"""Hub da base SIM: análises, problema, fonte e links."""

import streamlit as st

from catalog import TOPICS
from components.carousel import html_analises

API_SIM = (
    "https://apidadosabertos.saude.gov.br/vigilancia-e-meio-ambiente/"
    "sistema-de-informacao-sobre-mortalidade"
)
DOC_SIM = "https://datasus.saude.gov.br/mortalidade-desde-1996-pela-cid-10"


def render() -> None:
    """Página central da SIM, de onde saem os temas."""
    st.markdown("## SIM — Sistema de Informações sobre Mortalidade")
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
