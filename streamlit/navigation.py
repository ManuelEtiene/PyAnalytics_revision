"""Registro das páginas Streamlit e URLs da base SIM."""

import streamlit as st

from catalog import eh_tema_sim, slug_sim
from components.tema import params_extra

PAGES: dict = {}


def register(mapping: dict) -> None:
    """Guarda os objetos st.Page indexados por id do catálogo."""
    PAGES.clear()
    PAGES.update(mapping)


def page(page_id: str):
    """Retorna a página registrada para navegação."""
    return PAGES[page_id]


def href(page_id: str) -> str:
    """Caminho público (temas SIM: /sim?tema=retrato)."""
    return _com_tema(_caminho(page_id))


def _caminho(page_id: str) -> str:
    """URL do item, sem o parâmetro de tema. Home fica em /."""
    if eh_tema_sim(page_id):
        return f"/sim?tema={slug_sim(page_id)}"
    pag = page(page_id)
    path = str(getattr(pag, "url_path", None) or "").strip("/")
    return f"/{path}" if path else "/"


def _com_tema(url: str) -> str:
    """Acrescenta escuro=1 para o dark sobreviver ao <a href>."""
    extra = params_extra()
    if not extra:
        return url
    sep = "&" if "?" in url else "?"
    pares = "&".join(f"{chave}={valor}" for chave, valor in extra.items())
    return f"{url}{sep}{pares}"


def atalho(page_id: str) -> tuple:
    """Página e query para st.page_link (temas SIM ficam em /sim)."""
    if eh_tema_sim(page_id):
        pag, query = page("sim"), {"tema": slug_sim(page_id)}
    else:
        pag, query = page(page_id), {}
    query.update(params_extra())
    return pag, query or None


def link_pagina(page_id: str, label: str, icon: str | None = None) -> None:
    """st.page_link levando o tema na query."""
    pag, query = atalho(page_id)
    if icon:
        st.page_link(pag, label=label, icon=icon, query_params=query)
        return
    st.page_link(pag, label=label, query_params=query)


def abrir(page_id: str) -> None:
    """Troca de página; temas SIM usam /sim?tema=."""
    pag, query = atalho(page_id)
    if query:
        st.switch_page(pag, query_params=query)
        return
    st.switch_page(pag)


def redir_sim(tema: str):
    """Página-atalho das URLs antigas (/retrato → /sim?tema=retrato)."""

    def _run() -> None:
        query = {"tema": tema, **params_extra()}
        st.switch_page(page("sim"), query_params=query)

    _run.__name__ = f"redir_{tema.replace('-', '_')}"
    return _run
