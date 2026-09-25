"""Consulta de medicamentos e lugares no último mês."""

from __future__ import annotations

import pandas as pd


def ultimo_mes(df: pd.DataFrame) -> str:
    """Mês mais recente da base."""
    meses = df["ano_mes"].dropna()
    return "sem período" if meses.empty else str(meses.max())


def nomes_medicamentos(df: pd.DataFrame) -> list[str]:
    """Lista ordenada dos nomes para o combobox."""
    return sorted(df["material_nome_base"].dropna().astype(str).unique())


def recorte_mes(df: pd.DataFrame, medicamento: str, mes: str) -> pd.DataFrame:
    """Dispensações do medicamento no mês."""
    return df.loc[(df["ano_mes"] == mes) & (df["material_nome_base"] == medicamento)]


def tabela_lugares(df: pd.DataFrame) -> pd.DataFrame:
    """Quantidade por bairro no recorte."""
    base = df.loc[~df["bairro_malformado"]]
    if base.empty:
        return pd.DataFrame(columns=["Lugar", "Quantidade"])
    serie = base.groupby("bairro_padronizado")["quantidade"].sum()
    return _para_tabela(serie)


def _para_tabela(serie: pd.Series) -> pd.DataFrame:
    """Série lugar → quantidade em tabela pronta."""
    tabela = serie.sort_values(ascending=False).rename("Quantidade").reset_index()
    tabela.columns = ["Lugar", "Quantidade"]
    tabela["Quantidade"] = tabela["Quantidade"].astype(int)
    return tabela
