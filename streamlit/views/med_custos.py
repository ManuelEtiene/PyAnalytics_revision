"""Custos sobre as dispensações."""

from charts import med_custos as graficos
from data.prepare_med import load_med, periodo_med
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de custos (notebook Sprint 2)."""
    df = exige(load_med, "Nenhuma dispensação encontrada.")
    periodo = periodo_med(df)
    cabecalho(
        "O que os custos revelam sobre as dispensações?",
        f"Farmácia Básica · {periodo} · {len(df):,} registros · "
        f"R$ {df['custo_total'].sum():,.0f}".replace(",", "."),
        "medicamentos",
    )
    secao("Evolução mensal", graficos.evolucao_mensal(df, periodo))
    secao("Medicamentos que mais custam", graficos.top_custo(df, periodo))
    secao("Volume × custo", graficos.quantidade_vs_custo(df, periodo))
    secao("Fabricantes e classes", graficos.top_fabricantes(df, periodo), graficos.top_classes(df, periodo))
