"""Óbitos por local de ocorrência — gráficos na ordem do notebook."""

from charts import sim_local as graficos
from data.prepare_sim_local import load_local
from views.common import exige, periodo
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página completa, no mesmo modelo do Retrato."""
    sc, ara, tub = exige(load_local, "Nenhum óbito encontrado para esta análise.")
    periodo_txt = periodo(sc)
    cabecalho(
        "Óbitos por local de ocorrência",
        f"Ocorrência em SC · {periodo_txt} · {len(sc)} óbitos "
        f"(Araranguá: {len(ara)} · Tubarão: {len(tub)})",
    )
    _sc(sc, periodo_txt)
    _comparativo(sc, ara, tub, periodo_txt)


def _sc(sc, periodo_txt: str) -> None:
    """Gráficos 1 a 5 do notebook (recorte estadual)."""
    secao("Proporção de óbitos por local", graficos.proporcao_sc(sc, periodo_txt))
    secao("Idade por local", graficos.idade_por_local_sc(sc, periodo_txt))
    secao("Assistência médica", graficos.assistmed_sc(sc, periodo_txt))
    secao("Georreferenciamento", graficos.mapa_ocorrencia(sc, periodo_txt))
    secao("Causas por ambiente", graficos.causas_por_ambiente(sc, periodo_txt))


def _comparativo(sc, ara, tub, periodo_txt: str) -> None:
    """Gráficos 6 a 9: Araranguá × Tubarão × SC."""
    secao("Araranguá × Tubarão × SC", graficos.comparativo_local(ara, tub, sc, periodo_txt))
    secao("Idade em Araranguá vs SC", graficos.idade_ara_vs_sc(ara, sc, periodo_txt))
    secao("Amparo médico comparativo", graficos.assistmed_comparativo(ara, tub, sc, periodo_txt))
    secao("Óbitos normalizados pela população", graficos.taxa_populacao(ara, tub, sc, periodo_txt))
