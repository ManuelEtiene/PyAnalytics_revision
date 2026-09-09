"""Como as dispensações se distribuem entre bairros e centros de custo."""

from charts import med_bairro as graficos
from data.prepare_med import load_med, periodo_med
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Volume, CC, taxa per capita e comparativos (histórias 3 + revisado)."""
    df = exige(load_med, "Nenhuma dispensação encontrada.")
    periodo = periodo_med(df)
    cabecalho(
        "Como as dispensações se distribuem entre bairros e centros de custo?",
        f"Farmácia Básica · {periodo} · {len(df):,} registros",
        "medicamentos",
    )
    secao("Centros de custo", graficos.proporcao_cc(df, periodo), graficos.custo_por_cc(df, periodo))
    secao(
        "Bairros — maior e menor movimento",
        graficos.top_bairros(df, periodo),
        graficos.menores_bairros(df, periodo),
    )
    secao("Taxa por habitante (Censo 2022)", graficos.taxa_per_capita(df, periodo))
    secao("Comparativo de semestres", graficos.comparativo_semestres(df, periodo))
    secao(
        "Perfil por centro e bairro",
        graficos.perfil_tipo_cc(df, periodo),
        graficos.heatmap_bairro_tipo(df, periodo),
    )
