"""Retrato da mortalidade no município — gráficos do notebook."""

import streamlit as st

from charts import sim_cruzamentos as cruzamentos
from charts import sim_perfil as perfil
from charts import sim_territorio as territorio
from components.plot import plot, plot_or_caption
from views.common import load_or_stop, periodo
from views.sim_tema import cabecalho


def render() -> None:
    """Página completa do Retrato, em seções curtas."""
    df = load_or_stop()
    periodo_txt = periodo(df)
    cabecalho(
        "Retrato da mortalidade no município",
        f"Residentes de Araranguá · {periodo_txt} · {len(df)} óbitos",
    )
    _perfil(df, periodo_txt)
    _cruzamentos(df, periodo_txt)
    _territorio(df, periodo_txt)


def _perfil(df, periodo_txt: str) -> None:
    """Distribuições simples (tempo, idade, sexo, causa)."""
    st.markdown("### Perfil dos óbitos")
    for fig, insight in (
        perfil.obitos_por_ano(df, periodo_txt),
        perfil.media_por_mes(df, periodo_txt),
        perfil.obitos_por_faixa(df, periodo_txt),
        perfil.obitos_por_sexo(df, periodo_txt),
        perfil.obitos_por_raca(df, periodo_txt),
        perfil.obitos_por_escolaridade(df, periodo_txt),
        perfil.obitos_por_local(df, periodo_txt),
        perfil.top_causas(df, periodo_txt),
    ):
        plot(fig, insight)


def _cruzamentos(df, periodo_txt: str) -> None:
    """Heatmaps e ocupação — mesma ordem do notebook."""
    st.markdown("### Cruzamentos")
    plot_or_caption(*cruzamentos.escolaridade_por_faixa(df, periodo_txt))
    plot_or_caption(*cruzamentos.top_ocupacoes(df, periodo_txt))
    st.caption(
        "Renda não entra neste retrato: a Declaração de Óbito (SIM) não coleta "
        "remuneração. Escolaridade e ocupação são a aproximação socioeconômica."
    )
    plot_or_caption(*cruzamentos.sexo_por_local(df, periodo_txt))
    plot_or_caption(*cruzamentos.causas_por_faixa(df, periodo_txt))


def _territorio(df, periodo_txt: str) -> None:
    """Comparação com SC e município de ocorrência."""
    st.markdown("### Território")
    ano_min, ano_max = int(df["ANO_OBITO"].min()), int(df["ANO_OBITO"].max())
    fig, insight, _ = territorio.ranking_absoluto(ano_min, ano_max, periodo_txt)
    plot_or_caption(fig, insight)
    plot_or_caption(*territorio.ranking_taxa(ano_min, ano_max, periodo_txt))
    plot_or_caption(*territorio.ocorrencia_por_municipio(df, periodo_txt))
