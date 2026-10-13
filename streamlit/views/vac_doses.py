"""Tipos de dose e andamento."""

from charts import vac_doses as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de doses (notebook Sprint 3)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "O que as doses revelam sobre o andamento?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    secao("Textos de dose na base", graficos.ranking_dose_texto(df, periodo))
    secao("Categorias agrupadas", graficos.ranking_dose_grupo(df, periodo))
    secao("Categorias no tempo", graficos.evolucao_dose_grupo(df, periodo))
    secao("Na vacina líder", graficos.dose_por_vacina_lider(df, periodo))
