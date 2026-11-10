"""Gráficos: perfis de cuidado na farmácia básica (Card #16)."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts.texto import vazio
from charts.theme import PALETTE, abrevia, apply_layout, bar_horizontal


def volume_por_perfil(df: pd.DataFrame, periodo: str):
    """B1: Barras horizontais ordenadas do maior para o menor com percentagens e texto oficial."""
    serie = df["perfil_cuidado"].value_counts().sort_values(ascending=True)
    if serie.empty:
        return vazio()
    
    fig = bar_horizontal(serie, f"Medicamentos por perfil de cuidado — {periodo}", mostrar_pct=True)
    
    total = serie.sum()
    lider_nome = serie.index[-1]  # como está ordenado em ascending, o último é o maior
    lider_qtd = serie.iloc[-1]
    lider_pct = 100 * lider_qtd / total
    segundo_nome = serie.index[-2]
    segundo_pct = 100 * serie.iloc[-2] / total
    terceiro_nome = serie.index[-3]
    terceiro_pct = 100 * serie.iloc[-3] / total
    
    insight = (
        f"Entre agosto de 2025 e agosto de 2026 foram {total:,.0f} dispensações de medicamentos "
        "(retiradas, e não pessoas). Cardiovascular / Hipertensão lidera "
        f"({lider_qtd:,.0f}; {lider_pct:.1f}%), seguido de {segundo_nome.lower()} ({segundo_pct:.1f}%) "
        f"e {terceiro_nome.lower()} ({terceiro_pct:.1f}%): juntos, respondem por "
        f"{lider_pct + segundo_pct + terceiro_pct:.1f}%."
    ).replace(",", ".")
    
    return fig, insight


def top5_por_perfil_seletor(df: pd.DataFrame, periodo: str):
    """B4: Seletor de perfil com 5 barras e indicação de medicamentos por perfil."""
    base = df.copy()
    base["med"] = base["material_nome"].fillna("").astype(str)
    tabela = (
        base.groupby(["perfil_cuidado", "med"])
        .size()
        .reset_index(name="saidas")
        .sort_values(["perfil_cuidado", "saidas"], ascending=[True, False])
        .groupby("perfil_cuidado", group_keys=False)
        .head(5)
    )
    tabela["med"] = tabela["med"].str.split("-").str[0].str.strip()
    
    perfis_disponiveis = sorted(tabela["perfil_cuidado"].unique())
    if not perfis_disponiveis:
        st.info("Sem dados de perfis disponíveis.")
        return
    
    perfil_escolhido = st.selectbox("Escolha um grupo de cuidado:", perfis_disponiveis)
    
    sub = tabela[tabela["perfil_cuidado"] == perfil_escolhido]
    serie_bar = pd.Series(sub["saidas"].values, index=sub["med"].values).sort_values(ascending=True)
    
    fig = bar_horizontal(serie_bar, f"Top 5 medicamentos em {perfil_escolhido} — {periodo}", mostrar_pct=False)
    st.plotly_chart(fig, use_container_width=True)
    
    if "antibiótico" in perfil_escolhido.lower():
        st.caption("Nos antibióticos, amoxicilina + clavulanato destaca-se nas dispensações da rede.")
    else:
        st.caption("Valores refletem o volume total de saídas registadas na Farmácia Básica para o grupo selecionado.")