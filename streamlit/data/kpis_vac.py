"""KPIs da Home a partir das vacinações."""

from __future__ import annotations

import pandas as pd

from data.prepare_vac import load_vac, periodo_vac


def resumo_home_vac(df: pd.DataFrame | None = None) -> dict:
    """Indicadores chamativos da base Vacinações."""
    dados = df if df is not None else load_vac()
    com_data = dados.dropna(subset=["data_aplicacao"])
    top = com_data["nome_da_vacina"].value_counts()
    return {
        "total": int(len(dados)),
        "com_data": int(len(com_data)),
        "periodo": periodo_vac(com_data),
        "bairros": int(dados["bairro"].nunique()),
        "vacinas": int(dados["nome_da_vacina"].nunique()),
        "top_vacina": str(top.index[0]) if len(top) else "Sem dados",
        "top_n": int(top.iloc[0]) if len(top) else 0,
        "top_pct": float(100 * top.iloc[0] / len(com_data)) if len(com_data) else 0.0,
    }
