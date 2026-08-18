"""Entrada do Portal de Saúde — PyAnalytics / Araranguá."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Portal de Saúde — Araranguá",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from catalog import slug_sim
from components.chrome import inject_theme
from components.footer import render_footer
from components.header import render_header
from components.drawer import render_drawer
from navigation import redir_sim, register
from views import home, sim_hub, sobre

inject_theme()

# URLs antigas (/retrato) → /sim?tema=retrato
_ATALHOS = ("retrato", "evitavel", "onde_morrem", "violentas", "materna")


def _paginas() -> dict:
    """Mapa id do catálogo → st.Page (temas SIM vivem em /sim)."""
    paginas = {
        "home": st.Page(home.render, title="Início", default=True),
        "sobre": st.Page(sobre.render, title="Sobre o projeto PyAnalytics", url_path="sobre"),
        "sim": st.Page(sim_hub.render, title="SIM (Mortalidade)", url_path="sim"),
    }
    paginas.update(_redireciona_antigos())
    return paginas


def _redireciona_antigos() -> dict:
    """Mantém /retrato etc. apontando para o tema em /sim."""
    return {
        item_id: st.Page(
            redir_sim(slug_sim(item_id)),
            title=item_id,
            url_path=slug_sim(item_id),
            visibility="hidden",
        )
        for item_id in _ATALHOS
    }


paginas = _paginas()
register(paginas)
pg = st.navigation(list(paginas.values()), position="hidden")
render_header()
pg.run()
render_footer()
render_drawer()
