"""Mortalidade evitável e desigualdades sociais — ordem do notebook."""

from charts import sim_evitavel as graficos
from data.prepare_sim_evitavel import load_evitavel, taxas_por_grupo
from views.common import exige, periodo
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página completa, no mesmo modelo do Retrato."""
    df = exige(load_evitavel, "Nenhum óbito encontrado para esta análise.")
    periodo_txt = periodo(df)
    cabecalho(
        "Mortalidade evitável e desigualdades sociais",
        f"Residentes de Araranguá · {periodo_txt} · {len(df)} óbitos",
    )
    secao("Perfil demográfico", graficos.raca_por_sexo(df, periodo_txt))
    secao("Distribuição etária", graficos.distribuicao_idade(df, periodo_txt))
    secao("Grupos de causas", graficos.grupos_causa(df, periodo_txt), graficos.top_causas(df, periodo_txt))
    secao(
        "Desigualdades sociais",
        graficos.heatmap_raca_esc(df, periodo_txt),
        graficos.heatmap_causa_esc(df, periodo_txt),
    )
    secao(
        "Perfil do infarto",
        graficos.infarto_sexo(df, periodo_txt),
        graficos.infarto_faixa(df, periodo_txt),
    )
    secao("Comparação territorial", graficos.taxas_territorio(taxas_por_grupo(), periodo_txt))
