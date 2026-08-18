"""Mortes violentas na comunidade — gráficos na ordem do notebook."""

from charts import sim_violentas as graficos
from data.prepare_sim_violentas import load_violentas
from views.common import exige, periodo
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página completa, no mesmo modelo do Retrato."""
    df = exige(load_violentas, "Nenhuma morte violenta encontrada em Araranguá.")
    periodo_txt = periodo(df)
    cabecalho(
        "Mortes violentas na comunidade",
        f"Ocorrência em Araranguá · CID V–Y · {periodo_txt} · {len(df)} óbitos",
    )
    secao("Local e idade", graficos.volume_por_local(df, periodo_txt), graficos.idade_por_local(df, periodo_txt))
    secao("Amparo médico", graficos.assistmed_por_local(df, periodo_txt))
    secao("Georreferenciamento", graficos.taxa_sc(periodo_txt))
    secao("Diagnósticos por ambiente", graficos.top_causas_por_local(df, periodo_txt))
    _tipos(df, periodo_txt)


def _tipos(df, periodo_txt: str) -> None:
    """Acidentes, homicídios e principais causas."""
    secao(
        "Tipo de morte violenta",
        graficos.volume_por_tipo(df, periodo_txt),
        graficos.acidentes_por_local(df, periodo_txt),
        graficos.homicidios_por_local(df, periodo_txt),
        graficos.top_acidentes(df, periodo_txt),
        graficos.top_homicidios(df, periodo_txt),
    )
