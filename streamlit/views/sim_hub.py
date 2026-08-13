"""Hub da base SIM: problema, fonte e atalhos aos subtópicos."""

import streamlit as st

from catalog import TOPICS
from components.cards import topic_card
from navigation import page

API_SIM = (
    "https://apidadosabertos.saude.gov.br/vigilancia-e-meio-ambiente/"
    "sistema-de-informacao-sobre-mortalidade"
)
DOC_SIM = "https://datasus.saude.gov.br/mortalidade-desde-1996-pela-cid-10"


def render() -> None:
    """Página central da SIM, de onde saem os cinco tópicos."""
    st.markdown("## SIM — Sistema de Informações sobre Mortalidade")
    _problema()
    _base()
    _links()
    _topicos()


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
    st.page_link(page("sobre"), label="Sobre o PyAnalytics", icon=":material/info:")


def _topicos() -> None:
    """Grade com os cinco subtópicos da SIM."""
    st.markdown("### Análises")
    for linha in (TOPICS[:3], TOPICS[3:]):
        colunas = st.columns(len(linha))
        for coluna, item in zip(colunas, linha):
            status = "Disponível" if item.ready else "Em breve"
            with coluna:
                st.markdown(
                    topic_card("SIM", item.short, item.description, status),
                    unsafe_allow_html=True,
                )
                st.page_link(page(item.id), label="Abrir", icon=f":material/{item.icon}:")
