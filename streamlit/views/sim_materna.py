"""Saúde materna e infantil — gráficos na ordem do notebook."""

import streamlit as st

from charts import sim_materna as graficos
from data.prepare_sim_materna import load_materna
from views.common import exige, periodo
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página completa, no mesmo modelo do Retrato."""
    infantil, materno = exige(load_materna, "Nenhum óbito materno ou infantil encontrado.")
    periodo_txt = periodo(infantil if not infantil.empty else materno)
    cabecalho(
        "Saúde materna e infantil",
        f"Residentes de Araranguá · {periodo_txt} · "
        f"{len(infantil)} óbitos infantis · {len(materno)} óbitos maternos",
    )
    _infantil(infantil)
    _materno(materno)


def _infantil(df) -> None:
    """Blocos do notebook: prematuridade, parto, perfil e assistência."""
    _prematuridade(df)
    _nota_fetais(df)
    _historico(df)
    _parto(df)
    _perfil(df)
    _circunstancias(df)


def _prematuridade(df) -> None:
    """Primeiro bloco de óbitos infantis."""
    secao(
        "Óbitos infantis — prematuridade e extremos",
        graficos.idade_infantil(df),
        graficos.primeiros_meses(df),
        graficos.peso_vs_gestacao_inf(df),
        graficos.idade_vs_gestacao_inf(df),
    )


def _nota_fetais(df) -> None:
    """Mesma nota do notebook quando não há óbito fetal."""
    if "TIPOBITO" not in df.columns:
        return
    n = int((df["TIPOBITO"] == "Óbito Fetal").sum())
    if n == 0:
        st.caption("Não há registros de óbitos fetais neste recorte.")


def _historico(df) -> None:
    """Idade, mãe, gestação e sexo."""
    secao(
        "Análise histórica",
        graficos.idade_infantil_completa(df),
        graficos.idade_mae(df),
        graficos.semanas_gestacao(df),
        graficos.idade_por_sexo(df),
    )


def _parto(df) -> None:
    """Condições de parto, gravidez e peso."""
    secao(
        "Condições de parto e gravidez",
        graficos.semanas_por_parto(df),
        graficos.parto_vs_momento(df),
        graficos.heatmap_parto_peso(df),
        graficos.heatmap_parto_gravidez(df),
        graficos.momento_vs_parto(df),
        graficos.gravidez_vs_parto(df),
        graficos.peso_por_momento(df),
        graficos.peso_por_parto(df),
        graficos.media_peso_gravidez(df),
        graficos.momento_obito(df),
        graficos.gravidez_vs_gestacao(df),
        graficos.tempo_gestacao(df),
    )


def _perfil(df) -> None:
    """Escolaridade e idade da mãe."""
    secao(
        "Perfil socioeconômico",
        graficos.mae_vs_peso(df),
        graficos.mae_vs_semanas(df),
        graficos.escolaridade_mae(df),
    )


def _circunstancias(df) -> None:
    """Assistência médica nos óbitos infantis."""
    secao(
        "Período e circunstâncias",
        graficos.heatmap_tipo_assist(df),
        graficos.assist_por_tipo(df),
        graficos.assist_por_local(df),
    )


def _materno(df) -> None:
    """Histograma e série de idade — sem dispersões (peso/semana não se aplicam)."""
    secao(
        "Óbitos maternos",
        graficos.idade_materna(df),
        graficos.idade_materna_linha(df),
    )
