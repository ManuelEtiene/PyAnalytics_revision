"""Catálogo de páginas, bases e tópicos do portal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavItem:
    """Item navegável (home, hub, tópico ou sobre)."""

    id: str
    title: str
    short: str
    description: str
    keywords: tuple[str, ...]
    ready: bool = True
    icon: str = "description"
    group: str = ""


HOME = NavItem(
    id="home",
    title="Início",
    short="Início",
    description="Indicadores e atalhos para as bases públicas de Araranguá.",
    keywords=("home", "inicio", "início", "painel"),
    icon="dashboard",
)

SOBRE = NavItem(
    id="sobre",
    title="Sobre o projeto PyAnalytics",
    short="Sobre",
    description="PyAnalytics: dados públicos acessíveis à população.",
    keywords=("sobre", "projeto", "ufsc", "pyanalytics"),
    icon="info",
)

SIM_HUB = NavItem(
    id="sim",
    title="SIM (Mortalidade)",
    short="SIM",
    description="Sistema de Informações sobre Mortalidade — DATASUS.",
    keywords=("sim", "mortalidade", "obito", "óbito", "datasus"),
    icon="folder_open",
    group="SIM",
)

MEDICAMENTOS = NavItem(
    id="medicamentos",
    title="Medicamentos",
    short="Medicamentos",
    description="Dispensação e acesso a medicamentos em Araranguá.",
    keywords=("medicamentos", "farmacia", "farmácia", "dispensacao"),
    ready=False,
    icon="medication",
    group="Medicamentos",
)


def bases() -> tuple[NavItem, ...]:
    """Bases da Home: uma carta por dataset."""
    return (SIM_HUB, MEDICAMENTOS)


TOPICS = (
    NavItem(
        id="retrato",
        title="Retrato da mortalidade no município",
        short="Retrato",
        description="Perfil geral dos óbitos de residentes em Araranguá.",
        keywords=("retrato", "perfil", "municipio", "município", "geral", "sim"),
        icon="analytics",
        group="SIM",
    ),
    NavItem(
        id="evitavel",
        title="Mortalidade evitável e desigualdades sociais",
        short="Mortes evitáveis",
        description="Óbitos evitáveis e diferenças sociais na mortalidade.",
        keywords=("evitavel", "evitável", "desigualdade", "escolaridade", "sim"),
        ready=False,
        icon="balance",
        group="SIM",
    ),
    NavItem(
        id="onde_morrem",
        title="Óbitos por local de ocorrência",
        short="Local de óbito",
        description="Hospital, domicílio, via pública e comparação regional.",
        keywords=("onde", "local", "hospital", "domicilio", "domicílio", "sim"),
        icon="location_on",
        group="SIM",
    ),
    NavItem(
        id="violentas",
        title="Mortes violentas na comunidade",
        short="Mortes violentas",
        description="Causas externas: acidentes, agressões e suicídios.",
        keywords=("violentas", "agressao", "acidente", "sim"),
        icon="report",
        group="SIM",
    ),
    NavItem(
        id="materna",
        title="Saúde materna e infantil",
        short="Materna e infantil",
        description="Óbitos maternos, fetais e de crianças.",
        keywords=("materna", "infantil", "gestante", "bebe", "bebê", "sim"),
        icon="child_care",
        group="SIM",
    ),
)


def all_items() -> tuple[NavItem, ...]:
    """Páginas visíveis na busca e no menu."""
    return (HOME, SOBRE, SIM_HUB, *TOPICS)


def get_item(item_id: str) -> NavItem:
    """Retorna um item do catálogo pelo id."""
    for item in all_items():
        if item.id == item_id:
            return item
    raise KeyError(item_id)


def eh_tema_sim(item_id: str) -> bool:
    """True se o item é um tópico da base SIM (não a visão geral)."""
    return any(item.id == item_id for item in TOPICS)


def slug_sim(item_id: str) -> str:
    """Slug do tema na URL (/sim?tema=onde-morrem)."""
    return item_id.replace("_", "-")


def search_items(query: str) -> list[NavItem]:
    """Filtra páginas por título, descrição ou palavras-chave."""
    termo = query.strip().lower()
    if not termo:
        return []
    return [item for item in all_items() if _matches(item, termo)]


def _matches(item: NavItem, termo: str) -> bool:
    """Indica se o termo aparece no item."""
    blob = " ".join((item.title, item.short, item.description, *item.keywords))
    return termo in blob.lower()
