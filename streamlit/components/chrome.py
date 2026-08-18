"""Injeta o CSS do design no app (claro / escuro)."""

import re
from pathlib import Path

import streamlit as st

from components.tema import hidratar, persistir

_STYLES = Path(__file__).resolve().parents[1] / "styles"
_FLAG = "html:has(.pya-flag-escuro) "
_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Hanken+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap"
)


def inject_theme() -> None:
    """Flag no DOM + CSS; escuro só com html:has(.pya-flag-escuro)."""
    escuro = hidratar()
    claro = _css_seguro((_STYLES / "theme.css").read_text())
    escuro_css = _css_seguro(_escopo_escuro((_STYLES / "dark.css").read_text()))
    css = f"@import url('{_FONTS}');\n{claro}\n{escuro_css}"
    flag = "pya-flag-escuro" if escuro else "pya-flag-claro"
    st.markdown(f'<span class="{flag}" hidden></span>', unsafe_allow_html=True)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    persistir()


def _css_seguro(css: str) -> str:
    """Tira comentários e aspas duplas — quebram o HTML do st.markdown."""
    sem_comentarios = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    return sem_comentarios.replace('"', "'").replace("</", r"<\/")


def _escopo_escuro(css: str) -> str:
    """Prefixa seletores para o dark não sobrar no modo claro."""
    pedacos = []
    for regra in css.split("}"):
        pedacos.append(_prefixar_regra(regra))
    return "".join(pedacos)


def _prefixar_regra(regra: str) -> str:
    """Uma regra CSS; devolve vazia se não houver seletor."""
    if "{" not in regra:
        return regra
    sels, corpo = regra.rsplit("{", 1)
    if not sels.strip() or sels.strip().startswith("@"):
        return regra + "}"
    novos = [_um_seletor(s.strip()) for s in sels.split(",") if s.strip()]
    return ",\n".join(novos) + " {" + corpo + "}"


def _um_seletor(sel: str) -> str:
    """html vira a própria flag; o restante fica descendente dela."""
    if "pya-flag-escuro" in sel:
        return sel
    if sel == "html":
        return "html:has(.pya-flag-escuro)"
    return _FLAG + sel
