"""Caminhos do repositório e do cache local do portal."""

from pathlib import Path

CSV_NAME = "sim_sc_processado_analitico.csv"


def streamlit_dir() -> Path:
    """Pasta `streamlit/` do projeto."""
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    """Raiz do repositório (contém `data/` e `README.md`)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "data" / "processed").exists() and (parent / "README.md").exists():
            return parent
    return here.parents[2]


def csv_sim() -> Path:
    """CSV analítico do SIM usado pelo dashboard."""
    return repo_root() / "data" / "processed" / CSV_NAME


def cache_dir() -> Path:
    """Pasta de lookups baixados (CID, municípios, CBO)."""
    pasta = streamlit_dir() / ".cache"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta
