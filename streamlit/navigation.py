"""Registro das páginas Streamlit para troca via st.switch_page."""

PAGES: dict = {}


def register(mapping: dict) -> None:
    """Guarda os objetos st.Page indexados por id do catálogo."""
    PAGES.clear()
    PAGES.update(mapping)


def page(page_id: str):
    """Retorna a página registrada para navegação."""
    return PAGES[page_id]


def href(page_id: str) -> str:
    """Caminho da página (ex.: /sim, /retrato)."""
    pag = page(page_id)
    path = getattr(pag, "url_path", None) or page_id.replace("_", "-")
    return f"/{str(path).lstrip('/')}"
