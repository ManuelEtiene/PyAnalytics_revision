"""Origem do registro da aplicação."""

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
    secao("Volume por origem", graficos.ranking_origem(df, periodo))
    secao("No tempo", graficos.evolucao_origem(df, periodo))
    secao("Bairro × origem", graficos.origem_por_bairro(df, periodo))
