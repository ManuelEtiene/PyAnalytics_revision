"""Caminhos do repositório e do cache local do portal."""

from pathlib import Path

CSV_NAME = "sim_sc_processado_analitico.csv"
CSV_STEM = CSV_NAME.removesuffix(".csv")
CSV_DISPENSACAO = "dispensacao_analitico.csv"
CSV_CENSO_BAIRROS = "ararangua_bairros_ibge_censo2022_normalizacao.csv"


def streamlit_dir() -> Path:
    """Raiz do app Streamlit (este repositório)."""
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    """Raiz do repositório (contém `data/processed/` e `README.md`)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "data" / "processed").exists() and (parent / "README.md").exists():
            return parent
    return streamlit_dir()


def pasta_processed() -> Path:
    """Diretório preferencial dos CSVs (SIM e medicamentos)."""
    return repo_root() / "data" / "processed"


def _pastas_dados() -> list[Path]:
    """Candidatos: pasta do app e `data/processed` do monorepo PyAnalytics."""
    vistas: list[Path] = []
    for pasta in (
        pasta_processed(),
        streamlit_dir().parent / "data" / "processed",
        streamlit_dir() / "data" / "processed",
    ):
        if pasta not in vistas:
            vistas.append(pasta)
    return vistas


def _acha(nome: str) -> Path | None:
    """Primeiro caminho existente com o arquivo pedido."""
    for pasta in _pastas_dados():
        caminho = pasta / nome
        if caminho.exists():
            return caminho
    return None


def csv_sim_parts() -> list[Path]:
    """Pedaços do CSV analítico, em ordem (part001, part002, …)."""
    for pasta in _pastas_dados():
        partes = sorted(pasta.glob(f"{CSV_STEM}.part*.csv"))
        if partes:
            return partes
        unico = pasta / CSV_NAME
        if unico.exists():
            return [unico]
    return []


def csv_sim() -> Path:
    """Primeiro arquivo do SIM (pedaço ou CSV único) — usado só para cabeçalho."""
    partes = csv_sim_parts()
    if partes:
        return partes[0]
    return pasta_processed() / CSV_NAME


def cache_dir() -> Path:
    """Pasta de lookups baixados (CID, municípios, CBO)."""
    pasta = streamlit_dir() / ".cache"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def csv_dispensacao() -> Path:
    """CSV analítico de dispensação de medicamentos."""
    return _acha(CSV_DISPENSACAO) or (pasta_processed() / CSV_DISPENSACAO)


def csv_censo_bairros() -> Path:
    """População por bairro (Censo IBGE 2022) para taxas per capita."""
    return _acha(CSV_CENSO_BAIRROS) or (pasta_processed() / CSV_CENSO_BAIRROS)
