"""Registro das páginas Streamlit para troca via st.switch_page."""

PAGES: dict = {}


def register(mapping: dict) -> None:
    """Guarda os objetos st.Page indexados por id do catálogo."""
    PAGES.clear()
    PAGES.update(mapping)


def page(page_id: str):
    """Retorna a página registrada para navegação."""
    return PAGES[page_id]
