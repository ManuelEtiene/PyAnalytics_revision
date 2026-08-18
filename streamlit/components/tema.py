"""Tema claro/escuro: sobrevive a troca de página e F5."""

import streamlit as st

_COOKIE = "pya_tema"
_QUERY = "escuro"
_STATE = "tema_escuro"


def hidratar() -> bool:
    """Na sessão nova, lê a URL ou o cookie."""
    if _STATE not in st.session_state:
        st.session_state[_STATE] = _da_url() or _do_cookie()
    return bool(st.session_state[_STATE])


def ativo() -> bool:
    """True quando o modo escuro está ligado."""
    return bool(st.session_state.get(_STATE))


def alternar() -> None:
    """Inverte o tema e recarrega."""
    st.session_state[_STATE] = not st.session_state.get(_STATE, False)
    st.rerun()


def persistir() -> None:
    """Grava o cookie para a próxima navegação."""
    _gravar_cookie()


def params_extra() -> dict:
    """Query para os links levarem o tema junto."""
    return {_QUERY: "1"} if ativo() else {}


def _da_url() -> bool:
    """True se a URL pede escuro=1."""
    return st.query_params.get(_QUERY, "") == "1"


def _do_cookie() -> bool:
    """True se o cookie gravou o tema escuro."""
    cookies = getattr(st.context, "cookies", None) or {}
    return cookies.get(_COOKIE, "") == "escuro"


def _gravar_cookie() -> None:
    """Espelha o tema no cookie (próxima navegação lê)."""
    valor = "escuro" if ativo() else "claro"
    script = (
        "<script>try{parent.document.cookie="
        f"'{_COOKIE}={valor};path=/;max-age=31536000;SameSite=Lax'"
        "}catch(e){document.cookie="
        f"'{_COOKIE}={valor};path=/;max-age=31536000;SameSite=Lax'"
        "}</script>"
    )
    with st.container(key="pya_cookie"):
        st.iframe(script, height=1, width=1)
