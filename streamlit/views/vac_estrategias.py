"""Estratégias de vacinação."""

from charts import vac_estrategias as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de estratégias (notebook Sprint 3)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "Quais estratégias de vacinação aparecem?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    secao("Frequência das estratégias", graficos.ranking_estrategias(df, periodo))
    secao("No tempo", graficos.evolucao_estrategias(df, periodo))
    secao("Vacina × estratégia", graficos.cruzamento_vacina_estrategia(df, periodo))
    secao("Estratégias menos frequentes", graficos.estrategias_raras(df, periodo))
