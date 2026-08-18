"""KPIs da tela inicial a partir do Retrato."""

from __future__ import annotations

import pandas as pd

from data.prepare_sim_retrato import periodo_titulo


def total_obitos(df: pd.DataFrame) -> int:
    """Quantidade de óbitos no recorte."""
    return int(len(df))


def pct_hospital(df: pd.DataFrame) -> float:
    """Percentual de óbitos em hospital."""
    if df.empty:
        return 0.0
    return 100.0 * (df["LOCOCOR"] == "Hospital").mean()


def causa_principal(df: pd.DataFrame) -> tuple[str, int, float]:
    """Causa mais frequente, contagem e percentual."""
    if df.empty:
        return ("Sem dados", 0, 0.0)
    contagem = df["CAUSABAS_DESC"].value_counts()
    nome = str(contagem.index[0])
    n = int(contagem.iloc[0])
    pct = 100.0 * n / len(df)
    return nome, n, pct


def resumo_home(df: pd.DataFrame) -> dict:
    """Pacote de indicadores da Home."""
    causa, n_causa, pct_causa = causa_principal(df)
    return {
        "total": total_obitos(df),
        "periodo": periodo_titulo(df),
        "pct_hospital": pct_hospital(df),
        "causa": causa,
        "n_causa": n_causa,
        "pct_causa": pct_causa,
    }
