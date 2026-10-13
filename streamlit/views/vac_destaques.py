"""Vacinas em destaque nas aplicações."""

from charts import vac_destaques as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de destaques (notebook Sprint 3)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "Quais vacinas se destacam nas aplicações?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    secao("Ranking de aplicações", graficos.ranking_vacinas(df, periodo))
    secao("Concentração", graficos.concentracao(df, periodo))
    secao("Na estratégia líder", graficos.ranking_por_estrategia(df, periodo))
    secao("Evolução dos líderes", graficos.evolucao_lideres(df, periodo))
