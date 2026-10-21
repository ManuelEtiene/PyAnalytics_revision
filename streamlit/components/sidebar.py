"""Reexporta o drawer (evita cache antigo do Streamlit neste módulo)."""

from components.drawer import (
    fechar_se_mudou_pagina,
    nova_geracao_menu,
    render_drawer,
    render_menu_links,
)

__all__ = [
    "fechar_se_mudou_pagina",
    "nova_geracao_menu",
    "render_drawer",
    "render_menu_links",
]
