"""Distribuição por bairro da pessoa vacinada."""

import streamlit as st

from charts import vac_bairros as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página territorial (notebook Sprint 3)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "Como se distribuem entre os bairros?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    st.caption(
        "O bairro é o da pessoa vacinada na base — não indica a unidade onde a dose foi aplicada."
    )
    secao("Volume por bairro", graficos.ranking_bairros(df, periodo))
    secao("Tendência dos bairros líderes", graficos.evolucao_top_bairros(df, periodo))
    secao("Vacina líder por bairro", graficos.vacina_lider_por_bairro(df, periodo))
    secao("Peso da influenza por bairro", graficos.perfil_influenza_por_bairro(df, periodo))
