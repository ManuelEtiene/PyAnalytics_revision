"""Perfis de cuidado e tratamento na farmácia básica."""

import streamlit as st

from charts import med_destaques as graficos_destaques
from charts import med_perfis as graficos
from data.prepare_med import load_med, periodo_med
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de perfis e destaques da Farmácia Básica (Card #16)."""
    df = exige(load_med, "Nenhuma dispensação encontrada.")
    periodo = periodo_med(df)
    cabecalho(
        "Quais perfis de cuidado e tratamento aparecem?",
        f"Farmácia Básica · {periodo} · {len(df):,} registros",
        "medicamentos",
    )
    
    # B1: Distribuição dos perfis de cuidado (com percentagens e texto oficial)
    secao("Distribuição dos perfis", graficos.volume_por_perfil(df, periodo))
    
    # B4: Seletor interativo de Top 5 medicamentos por perfil de cuidado
    st.markdown("### Top 5 medicamentos por perfil")
    graficos.top5_por_perfil_seletor(df, periodo)
    
    # B5: Top 10 geral de medicamentos com nota oficial corrigida
    secao("Top 10 geral", graficos_destaques.top_saidas(df, periodo))
    
    # B6: Evolução mensal dos principais perfis com insight oficial
    secao("Evolução mensal", graficos_destaques.sazonalidade_tipo(df, periodo))