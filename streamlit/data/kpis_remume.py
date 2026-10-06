"""Destaque da Home a partir da REMUME (locais de dispensação)."""

from __future__ import annotations

import pandas as pd

from data.load_remume import load_remume


def resumo_home_remume(df: pd.DataFrame | None = None) -> dict:
    """Números para o card que leva à busca REMUME."""
    dados = df if df is not None else load_remume()
    so_farmacia = dados.loc[~dados["tem_ubs"]]
    return {
        "itens": int(len(dados)),
        "medicamentos": int(dados["nome_busca"].nunique()),
        "so_farmacia": int(len(so_farmacia)),
        "pct_so_farmacia": _pct(len(so_farmacia), len(dados)),
        "com_ubs": int(dados["tem_ubs"].sum()),
    }


def _pct(parte: int, total: int) -> float:
    """Percentual seguro."""
    return round(100.0 * parte / total, 1) if total else 0.0
