"""Origem do registro da aplicação."""

import streamlit as st
from charts import vac_origem as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de origem (notebook Sprint 3)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "O que a origem do registro revela?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    
    # C1: Volume por origem
    secao("Volume por origem", graficos.ranking_origem(df, periodo))
    st.markdown(
        "**Contexto da origem:** 'Origem do registro' indica onde o dado foi lançado no sistema. "
        "A base possui 30.883 registros de aplicação (fevereiro a junho de 2026). Em 30.023 deles a origem está informada: "
        "**8 em cada 10 (81,8%; 24.560)** vieram da **carteirinha**, **15,7% (4.722)** do **prontuário** e **2,5% (741)** da **tela de aplicação**."
    )
   # C2: No tempo
    secao("No tempo", graficos.evolucao_origem(df, periodo))
    st.markdown(
        "**Evolução temporal:** Em todos os meses, a maior parte dos registros vem da carteirinha (cerca de 75% a 85%). "
        "Ela cresce de fevereiro (cerca de 1.300) até abril (cerca de 7.300) e cai em maio e junho. "
        "O prontuário varia entre cerca de 300 e 1.300 por mês, e a tela de aplicação fica sempre abaixo de 250."
    )

    # C3: Bairro x origem
    secao("Bairro × origem", graficos.origem_por_bairro(df, periodo))
    st.markdown(
        "**Análise por bairro:** Cada barra mostra de onde vêm os registros de aplicação em um bairro. "
        "Em seis dos oito bairros mostrados, mais de 98% vêm da carteirinha. "
        "Em Jardim Cibele, 81% vêm do prontuário, e em Coloninha, 57%. "
        "A tela de aplicação quase não aparece nesses bairros (47 registros, em Bom Pastor)."
 )
    
   