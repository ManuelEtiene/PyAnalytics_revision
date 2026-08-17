"""Página institucional do PyAnalytics."""

import base64
from pathlib import Path

import streamlit as st

_REPO_LOGO = Path(__file__).resolve().parents[2] / "assets" / "IconPyAnalytics.png"
_LOCAL_LOGO = Path(__file__).resolve().parents[1] / "assets" / "pyanalytics.png"
LOGO = _REPO_LOGO if _REPO_LOGO.exists() else _LOCAL_LOGO

INTEGRANTES = (
    "Andréa Sabedra Bordin",
    "André Gaspar",
    "Nathália Geraldino Ribas",
    "Igor de Matos da Rosa",
    "João Vitor Caetano da Rosa",
    "Mirela Pedro Tereza",
    "Mamadjam Jalo",
    "João Pinto Ferreira",
    "Lucas Teixeira Belli",
    "Manuel Etiene da Silva João",
    "Esther de Olivera",
    "Beatriz Pereira Goulart",
)


def render() -> None:
    """Explica o projeto para o público, com base no README."""
    _titulo()
    st.markdown(
        "O **PyAnalytics** é um projeto de extensão da **UFSC — Campus Araranguá**. "
        "A ideia é simples: os dados de saúde já são públicos, mas quase ninguém "
        "consegue lê-los no formato bruto. Aqui eles viram painéis abertos para a "
        "população, gestores e a comunidade acadêmica."
    )
    _objetivos()
    _como_usar()
    _integrantes()


def _titulo() -> None:
    """Cabeçalho da página com o ícone do PyAnalytics."""
    imagem = base64.b64encode(LOGO.read_bytes()).decode()
    st.html(
        f"""
        <div class="pya-sobre-titulo">
          <img class="pya-sobre-logo" src="data:image/png;base64,{imagem}"
               alt="PyAnalytics" width="200" height="200">
          <h2>Sobre o projeto PyAnalytics</h2>
        </div>
        """
    )


def _objetivos() -> None:
    """Lista o que o projeto se propõe a fazer."""
    st.markdown("### O que fazemos")
    st.markdown(
        """
- Coletar e organizar **dados públicos** de interesse regional
- Tratar e analisar de forma **reproduzível**
- Publicar **visualizações claras** para a comunidade
- Manter o trabalho **aberto** a contribuições
        """
    )


def _como_usar() -> None:
    """Como navegar no portal e de onde vêm os dados."""
    st.markdown("### Como usar este portal")
    st.markdown(
        "A tela inicial mostra um retrato rápido. Pelo **menu** (ícone à esquerda) "
        "você escolhe a base — hoje a **SIM**, de mortalidade — e o subtópico. "
        "A **busca** no topo encontra o mesmo conteúdo pelo nome."
    )
    st.markdown("### Instituição")
    st.markdown(
        "**Universidade Federal de Santa Catarina (UFSC)**  \n"
        "Campus Araranguá — Projeto de Extensão PyAnalytics"
    )
    st.markdown(
        "Fonte dos óbitos: [SIM / Dados Abertos do Ministério da Saúde]"
        "(https://apidadosabertos.saude.gov.br/vigilancia-e-meio-ambiente/"
        "sistema-de-informacao-sobre-mortalidade)."
    )


def _integrantes() -> None:
    """Equipe do projeto de extensão."""
    st.markdown("### Integrantes")
    st.markdown("\n".join(f"- {nome}" for nome in INTEGRANTES))
