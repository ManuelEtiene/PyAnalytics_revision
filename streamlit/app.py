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

from components.chrome import inject_theme
from components.footer import render_footer
from components.header import render_header
from components.drawer import render_drawer
from navigation import register
from views import evitavel, home, local, materna, retrato, sim_hub, sobre, violentas

inject_theme()


def _paginas() -> dict:
    """Mapa id do catálogo → st.Page (url_path único por página)."""
    return {
        "home": st.Page(home.render, title="Início", default=True, url_path="inicio"),
        "sobre": st.Page(sobre.render, title="Sobre o projeto PyAnalytics", url_path="sobre"),
        "sim": st.Page(sim_hub.render, title="SIM (Mortalidade)", url_path="sim"),
        "retrato": st.Page(retrato.render, title="Retrato da mortalidade", url_path="retrato"),
        "evitavel": st.Page(evitavel.render, title="Mortalidade evitável", url_path="evitavel"),
        "onde_morrem": st.Page(local.render, title="Óbitos por local de ocorrência", url_path="onde-morrem"),
        "violentas": st.Page(violentas.render, title="Mortes violentas", url_path="violentas"),
        "materna": st.Page(materna.render, title="Saúde materna e infantil", url_path="materna"),
    }


paginas = _paginas()
register(paginas)
pg = st.navigation(list(paginas.values()), position="hidden")
render_header()
pg.run()
render_footer()
render_drawer()
