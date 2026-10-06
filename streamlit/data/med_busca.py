"""Consulta REMUME: apresentações e locais de dispensação (unidades/farmácia)."""

from __future__ import annotations

import pandas as pd

from data.load_remume import load_remume


def load_busca() -> pd.DataFrame:
    """Base da busca: REMUME processada (não usa bairro do paciente)."""
    return load_remume()


def total_itens(df: pd.DataFrame) -> int:
    """Quantidade de itens listados na REMUME."""
    return int(len(df))


def nomes_medicamentos(df: pd.DataFrame) -> list[str]:
    """Lista ordenada dos nomes para o combobox."""
    return sorted(df["nome_busca"].dropna().astype(str).unique())


def recorte(df: pd.DataFrame, medicamento: str) -> pd.DataFrame:
    """Apresentações do medicamento na REMUME."""
    return df.loc[df["nome_busca"] == medicamento].copy()


def tabela_apresentacoes(df: pd.DataFrame) -> pd.DataFrame:
    """Apresentações e tipo de unidade que dispensa."""
    if df.empty:
        return pd.DataFrame(columns=["Apresentação", "Categoria", "Dispensado em"])
    base = df.copy()
    base["Dispensado em"] = base.apply(_rotulo_acesso, axis=1)
    return (
        base[["apresentacao", "categoria", "Dispensado em"]]
        .rename(columns={"apresentacao": "Apresentação", "categoria": "Categoria"})
        .reset_index(drop=True)
    )


def tabela_lugares(df: pd.DataFrame) -> pd.DataFrame:
    """Unidades/farmácia que dispensam (REMUME), nunca endereço do paciente."""
    if df.empty:
        return pd.DataFrame(columns=["Unidade de dispensação", "Tipo"])
    linhas: list[dict[str, str]] = []
    vistos: set[str] = set()
    for texto in df["locais"].dropna().astype(str):
        for lugar in texto.split(" | "):
            lugar = lugar.strip()
            if not lugar or lugar in vistos:
                continue
            vistos.add(lugar)
            linhas.append(
                {
                    "Unidade de dispensação": lugar,
                    "Tipo": "Farmácia de referência" if "Bom Pastor" in lugar else "UBS",
                }
            )
    return pd.DataFrame(linhas)


def resumo(df: pd.DataFrame) -> dict[str, int | bool]:
    """Números rápidos do medicamento escolhido."""
    return {
        "apresentacoes": int(len(df)),
        "lugares": int(len(tabela_lugares(df))),
        "tem_farmacia": bool(df["tem_farmacia"].any()) if not df.empty else False,
        "tem_ubs": bool(df["tem_ubs"].any()) if not df.empty else False,
    }


def _rotulo_acesso(row: pd.Series) -> str:
    """Texto curto do local de dispensação na REMUME."""
    partes: list[str] = []
    if row.get("tem_farmacia"):
        partes.append("Farmácia Bom Pastor")
    if row.get("tem_ubs"):
        partes.append("UBS")
    return " e ".join(partes) if partes else str(row.get("local_bruto", ""))
