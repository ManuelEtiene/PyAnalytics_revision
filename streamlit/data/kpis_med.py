"""KPIs da Home a partir da dispensação de medicamentos."""

from __future__ import annotations

import pandas as pd

from data.prepare_med import load_med, periodo_med


def resumo_home_med(df: pd.DataFrame | None = None) -> dict:
    """Indicadores chamativos da base Medicamentos."""
    dados = df if df is not None else load_med()
    top = _top_custo(dados)
    return {
        "total": int(len(dados)),
        "periodo": periodo_med(dados),
        "custo_total": float(dados["custo_total"].sum()),
        "medicamentos": int(dados["material_nome_base"].nunique()),
        "top_med": top[0],
        "top_custo": top[1],
        "top_pct": top[2],
    }


def _top_custo(df: pd.DataFrame) -> tuple[str, float, float]:
    """Medicamento com maior custo acumulado."""
    if df.empty:
        return ("Sem dados", 0.0, 0.0)
    serie = df.groupby("material_nome_base")["custo_total"].sum().sort_values(ascending=False)
    nome = str(serie.index[0])
    valor = float(serie.iloc[0])
    pct = 100.0 * valor / float(df["custo_total"].sum()) if df["custo_total"].sum() else 0.0
    return nome, valor, pct
