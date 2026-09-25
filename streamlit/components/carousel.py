"""Grade HTML das análises da base SIM."""

from catalog import NavItem
from components.cards import analise_card
from navigation import href


def html_analises(itens: tuple[NavItem, ...]) -> str:
    """Grade de cards do mesmo tamanho."""
    pecas = "".join(_item(item) for item in itens)
    return f'<div class="sim-analises-grade">{pecas}</div>'


def _item(item: NavItem) -> str:
    """Um card: status conforme o tema estiver pronto."""
    status = "Disponível" if item.ready else "Em breve"
    corpo = analise_card(item.short, item.description, status, item.ready, item.kicker)
    inner = _envolver(item, corpo)
    return f'<div class="sim-analise-item">{inner}</div>'


def _envolver(item: NavItem, corpo: str) -> str:
    """Link para a página do tema (mesmo as ainda em breve)."""
    classe = "sim-analise-link" if item.ready else "sim-analise-link sim-analise-soon"
    return (
        f'<a class="{classe}" href="{href(item.id)}" target="_self">'
        f"{corpo}</a>"
    )
