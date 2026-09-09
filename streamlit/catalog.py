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
    icon="medication",
    group="Medicamentos",
)

VACINAS = NavItem(
    id="vacinas",
    title="Vacinações",
    short="Vacinações",
    description="Aplicações de vacinas em Araranguá (jan–jun/2026).",
    keywords=("vacina", "vacinas", "imunizacao", "imunização", "sala"),
    ready=False,
    icon="vaccines",
    group="Vacinações",
)


def bases() -> tuple[NavItem, ...]:
    """Bases da Home: uma carta por dataset."""
    return (SIM_HUB, MEDICAMENTOS, VACINAS)


TOPICS_SIM = (
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

TOPICS_MED = (
    NavItem(
        id="med_tempo",
        title="Como a dispensação muda ao longo do tempo?",
        short="No tempo",
        description="Variação de volume por período, padrões e mudanças inesperadas.",
        keywords=("tempo", "mes", "mês", "sazonal", "inverno", "verao", "verão", "medicamentos"),
        ready=False,
        icon="timeline",
        group="Medicamentos",
    ),
    NavItem(
        id="med_destaques",
        title="Quais medicamentos se destacam nas dispensações?",
        short="Destaques",
        description="Medicamentos com maior ou menor relevância na farmácia básica.",
        keywords=("destaque", "ranking", "saidas", "saídas", "medicamentos"),
        icon="star",
        group="Medicamentos",
    ),
    NavItem(
        id="med_bairro",
        title="Como se distribuem entre bairros e centros de custo?",
        short="Bairros e CC",
        description="Diferenças territoriais, centros de custo e taxas por habitante.",
        keywords=("bairro", "centro", "custo", "territorio", "território", "censo", "medicamentos"),
        icon="map",
        group="Medicamentos",
    ),
    NavItem(
        id="med_perfis",
        title="Quais perfis de cuidado e tratamento aparecem?",
        short="Perfis de cuidado",
        description="Reserva: classificação dos medicamentos por tema de cuidado.",
        keywords=("perfil", "cuidado", "tratamento", "classe", "medicamentos"),
        ready=False,
        icon="health_and_safety",
        group="Medicamentos",
    ),
    NavItem(
        id="med_custos",
        title="O que os custos revelam sobre as dispensações?",
        short="Custos",
        description="Relação entre quantidade, custo e relevância dos medicamentos.",
        keywords=("custo", "gasto", "orcamento", "orçamento", "fabricante", "medicamentos"),
        icon="payments",
        group="Medicamentos",
    ),
)

TOPICS_VAC = (
    NavItem(
        id="vac_tempo",
        title="Como as aplicações mudam ao longo do tempo?",
        short="No tempo",
        description="Picos, meses e variação do volume de aplicações.",
        keywords=("tempo", "mes", "mês", "pico", "influenza", "vacina"),
        ready=False,
        icon="timeline",
        group="Vacinações",
    ),
    NavItem(
        id="vac_destaques",
        title="Quais vacinas se destacam nas aplicações?",
        short="Destaques",
        description="Imunizantes com maior ou menor relevância na base.",
        keywords=("destaque", "ranking", "covid", "nirsevimabe", "vacina"),
        ready=False,
        icon="star",
        group="Vacinações",
    ),
    NavItem(
        id="vac_salas",
        title="Como se distribuem entre salas e bairros?",
        short="Salas e bairros",
        description="Diferenças de movimento entre territórios e salas.",
        keywords=("sala", "bairro", "territorio", "território", "ups", "vacina"),
        ready=False,
        icon="map",
        group="Vacinações",
    ),
    NavItem(
        id="vac_estrategias",
        title="Quais estratégias de vacinação aparecem?",
        short="Estratégias",
        description="Rotina, especial, pós-exposição e outras formas de vacinar.",
        keywords=("estrategia", "estratégia", "rotina", "bloqueio", "vacina"),
        ready=False,
        icon="flag",
        group="Vacinações",
    ),
    NavItem(
        id="vac_doses",
        title="O que as doses revelam sobre o andamento?",
        short="Doses",
        description="1ª dose, 2ª dose, reforço e dose única (sem seguir a pessoa).",
        keywords=("dose", "reforco", "reforço", "esquema", "vacina"),
        ready=False,
        icon="pin",
        group="Vacinações",
    ),
    NavItem(
        id="vac_origem",
        title="O que a origem do registro revela?",
        short="Origem",
        description="Carteirinha, prontuário ou tela de aplicação.",
        keywords=("origem", "carteirinha", "prontuario", "prontuário", "vacina"),
        ready=False,
        icon="edit_note",
        group="Vacinações",
    ),
    NavItem(
        id="vac_lotes",
        title="O que lotes e validades revelam?",
        short="Lotes e validade",
        description="Diversidade de lotes e prazo restante na aplicação.",
        keywords=("lote", "validade", "prazo", "estoque", "vacina"),
        ready=False,
        icon="inventory_2",
        group="Vacinações",
    ),
)

# Compat: hub SIM e menu antigo usam TOPICS = temas da mortalidade
TOPICS = TOPICS_SIM


def all_items() -> tuple[NavItem, ...]:
    """Páginas visíveis na busca e no menu."""
    return (
        HOME,
        SOBRE,
        SIM_HUB,
        MEDICAMENTOS,
        VACINAS,
        *TOPICS_SIM,
        *TOPICS_MED,
        *TOPICS_VAC,
    )


def get_item(item_id: str) -> NavItem:
    """Retorna um item do catálogo pelo id."""
    for item in all_items():
        if item.id == item_id:
            return item
    raise KeyError(item_id)


def eh_tema_sim(item_id: str) -> bool:
    """True se o item é um tópico da base SIM."""
    return any(item.id == item_id for item in TOPICS_SIM)


def eh_tema_med(item_id: str) -> bool:
    """True se o item é um tópico da base Medicamentos."""
    return any(item.id == item_id for item in TOPICS_MED)


def eh_tema_vac(item_id: str) -> bool:
    """True se o item é um tópico da base Vacinações."""
    return any(item.id == item_id for item in TOPICS_VAC)


def slug_sim(item_id: str) -> str:
    """Slug do tema SIM na URL (/sim?tema=onde-morrem)."""
    return item_id.replace("_", "-")


def slug_med(item_id: str) -> str:
    """Slug do tema Medicamentos (/medicamentos?tema=bairro-cc)."""
    mapa = {
        "med_tempo": "tempo",
        "med_destaques": "destaques",
        "med_bairro": "bairro-cc",
        "med_perfis": "perfis",
        "med_custos": "custos",
    }
    return mapa.get(item_id, item_id.replace("_", "-").removeprefix("med-"))


def slug_vac(item_id: str) -> str:
    """Slug do tema Vacinações (/vacinas?tema=salas-bairros)."""
    mapa = {
        "vac_tempo": "tempo",
        "vac_destaques": "destaques",
        "vac_salas": "salas-bairros",
        "vac_estrategias": "estrategias",
        "vac_doses": "doses",
        "vac_origem": "origem",
        "vac_lotes": "lotes",
    }
    return mapa.get(item_id, item_id.replace("_", "-").removeprefix("vac-"))


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
