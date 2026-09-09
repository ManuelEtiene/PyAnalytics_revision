"""Medicamentos em destaque na dispensação."""

from charts import med_destaques as graficos
from data.prepare_med import load_med, periodo_med
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de destaques (notebook Sprint 2)."""
    df = exige(load_med, "Nenhuma dispensação encontrada.")
    periodo = periodo_med(df)
    cabecalho(
        "Quais medicamentos se destacam nas dispensações?",
        f"Farmácia Básica · {periodo} · {len(df):,} registros",
        "medicamentos",
    )
    secao("Ranking de saídas", graficos.top_saidas(df, periodo))
    secao("Evolução dos líderes", graficos.evolucao_top5(df, periodo))
    secao("Tipos de tratamento", graficos.tipos_tratamento(df, periodo))
    secao("Bairros e quantidade média", graficos.top_bairros_saidas(df, periodo), graficos.media_quantidade(df, periodo))
    secao("Sazonalidade", graficos.sazonalidade_tipo(df, periodo))
