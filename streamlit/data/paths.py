"""Caminhos do repositório e do cache local do portal."""

from pathlib import Path

CSV_NAME = "sim_sc_processado_analitico.csv"
CSV_STEM = CSV_NAME.removesuffix(".csv")


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
    """Diretório dos CSVs processados do SIM."""
    return repo_root() / "data" / "processed"


def csv_sim_parts() -> list[Path]:
    """Pedaços do CSV analítico, em ordem (part001, part002, …)."""
    partes = sorted(pasta_processed().glob(f"{CSV_STEM}.part*.csv"))
    if partes:
        return partes
    unico = pasta_processed() / CSV_NAME
    return [unico] if unico.exists() else []


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
