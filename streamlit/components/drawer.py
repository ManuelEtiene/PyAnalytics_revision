"""Menu lateral em drawer fixo na tela (não no fluxo da página)."""

from urllib.parse import urlparse

import streamlit as st

from catalog import TOPICS_MED, TOPICS_SIM, TOPICS_VAC
from navigation import abrir


def render_drawer() -> None:
    """Painel esquerdo, só enquanto o hambúrguer estiver aberto."""
    if not st.session_state.get("menu_aberto"):
        return
    ignorar = st.session_state.pop("_menu_acabou_de_abrir", False)
    _fundo(ignorar)
    with st.container(key="pya_drawer", border=False):
        render_menu_links(ignorar)


def nova_geracao_menu() -> None:
    """Troca as chaves dos botões para o clique antigo não repetir."""
    st.session_state._menu_geracao = st.session_state.get("_menu_geracao", 0) + 1


def fechar_se_mudou_pagina() -> None:
    """Fecha o menu ao navegar; o estado senão permanece nas outras páginas."""
    atual = _url_atual()
    anterior = st.session_state.get("_menu_url")
    st.session_state._menu_url = atual
    if anterior is None or anterior == atual:
        return
    st.session_state.menu_aberto = False


def _url_atual() -> str:
    """Caminho + tema da página corrente."""
    bruto = str(getattr(st.context, "url", "") or "")
    caminho = urlparse(bruto).path.rstrip("/") or "/"
    tema = str(st.query_params.get("tema", ""))
    return f"{caminho}?tema={tema}"


def _geracao() -> int:
    return int(st.session_state.get("_menu_geracao", 0))


def _fundo(ignorar: bool) -> None:
    """Camada atrás do menu: clique fora fecha sem seguir outro link."""
    with st.container(key="pya_menu_overlay"):
        chave = f"fechar_menu_overlay_{_geracao()}"
        if not st.button("Fechar menu", key=chave, type="tertiary"):
            return
        if ignorar:
            return
        st.session_state.menu_aberto = False
        st.rerun()


def render_menu_links(ignorar: bool = False) -> None:
    """Seções Geral e Datasets."""
    _secao_geral(ignorar)
    _secao_datasets(ignorar)


def _secao_geral(ignorar: bool) -> None:
    """Início e Sobre o projeto."""
    st.markdown("**Geral**")
    _item("home", "Início", ":material/dashboard:", ignorar)
    _item("sobre", "Sobre PyAnalytics", ":material/info:", ignorar)


def _secao_datasets(ignorar: bool) -> None:
    """Pastas das bases com visão geral e temas."""
    st.markdown("**Datasets**")
    _pasta("SIM (Mortalidade)", "sim", TOPICS_SIM, "folder_open", ignorar)
    _pasta("Medicamentos", "medicamentos", TOPICS_MED, "medication", ignorar)
    _pasta("Vacinações", "vacinas", TOPICS_VAC, "vaccines", ignorar)


def _pasta(titulo: str, hub_id: str, topicos, icone: str, ignorar: bool) -> None:
    """Expander com visão da base e subtópicos."""
    with st.expander(titulo, expanded=False):
        _item(hub_id, "Visão da base", f":material/{icone}:", ignorar)
        for topico in topicos:
            _item(topico.id, _rotulo(topico), f":material/{topico.icon}:", ignorar)


def _rotulo(topico) -> str:
    """Busca usa o nome curto; análises ficam com o título completo."""
    return topico.short if topico.id == "med_busca" else topico.title


def _item(page_id: str, label: str, icon: str, ignorar: bool) -> None:
    """Atalho do menu; chave nova a cada abertura evita clique fantasma."""
    chave = f"menu_item_{_geracao()}_{page_id}"
    if not st.button(label, key=chave, icon=icon, type="tertiary"):
        return
    if ignorar:
        return
    abrir(page_id)
