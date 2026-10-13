"""Aplicações de vacinas ao longo do tempo."""

import streamlit as st

from charts import vac_tempo as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página temporal (notebook Sprint 3 — vacinas no tempo)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "Como as aplicações mudam ao longo do tempo?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    secao("Volume mensal", graficos.volume_mensal(df, periodo))
    secao("Influenza e demais vacinas", graficos.influenza_vs_outras(df, periodo))
    secao("Vacinas mais aplicadas", graficos.top_vacinas_no_tempo(df, periodo))
    secao("Vacinas menos frequentes", graficos.vacinas_menos_frequentes(df, periodo))
    secao("Estratégias no tempo", graficos.estrategias_no_tempo(df, periodo))
    secao("Bairros no tempo", graficos.bairros_no_tempo(df, periodo))
    st.caption(
        "Os números são aplicações registradas — não cobertura da população, "
        "nem diagnóstico de surto ou necessidade de saúde."
    )
