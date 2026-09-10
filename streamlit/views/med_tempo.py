"""Dispensação de medicamentos ao longo do tempo."""

import streamlit as st

from charts import med_tempo as graficos
from data.prepare_med import load_med, periodo_med
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página temporal (notebook Sprint 2)."""
    df = exige(load_med, "Nenhuma dispensação encontrada.")
    periodo = periodo_med(df)
    cabecalho(
        "Como a dispensação muda ao longo do tempo?",
        f"Farmácia Básica · {periodo} · {len(df):,} registros",
        "medicamentos",
    )
    secao("Volume mensal da rede", graficos.volume_mensal_geral(df, periodo))
    secao("Padrão diário e anomalias", graficos.padrao_diario_rede(df, periodo))
    anom, fer = graficos.tabelas_anomalias(df)
    if not anom.empty or not fer.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Anomalias de volume**")
            st.dataframe(anom, hide_index=True, width='stretch')
        with c2:
            st.markdown("**Possíveis feriados**")
            st.dataframe(fer, hide_index=True, width='stretch')
    secao(
        "Por tipo de material",
        graficos.tendencia_mensal_coluna(df, "material_tipo", periodo, n=4),
    )
    secao(
        "Por bairro (índice base 100)",
        graficos.tendencia_mensal_coluna(df.loc[~df["bairro_malformado"]], "bairro_padronizado", periodo, n=8),
    )
    secao(
        "Por centro de custo",
        graficos.tendencia_mensal_coluna(df, "centro_custo_nome", periodo, n=4),
    )
    secao(
        "Por classe terapêutica",
        graficos.tendencia_mensal_coluna(df, "classe_terapeutica", periodo, n=5),
        graficos.top5_classes_linha(df, periodo),
    )
    secao(
        "Medicamentos (nome base)",
        graficos.tendencia_mensal_coluna(df, "material_nome_base", periodo, n=6),
    )
    st.markdown("### Ranking completo de bairros")
    st.dataframe(graficos.tabela_resumo_bairro(df), hide_index=True, width='stretch')
    st.caption("Um ciclo anual na base: sazonalidade entre anos ainda não pode ser confirmada.")
