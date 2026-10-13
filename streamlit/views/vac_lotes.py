"""Lotes e prazos de validade."""

from charts import vac_lotes as graficos
from data.prepare_vac import load_vac, periodo_vac
from views.common import exige
from views.sim_tema import cabecalho, secao


def render() -> None:
    """Página de lotes (notebook Sprint 3)."""
    df = exige(load_vac, "Nenhuma vacinação encontrada.")
    periodo = periodo_vac(df)
    cabecalho(
        "O que lotes e validades revelam?",
        f"Araranguá · {periodo} · {len(df):,} registros".replace(",", "."),
        "vacinas",
    )
    secao("Diversidade por vacina", graficos.diversidade_lotes_vacina(df, periodo))
    secao("Diversidade por bairro", graficos.diversidade_lotes_bairro(df, periodo))
    secao("Lotes mais usados", graficos.lotes_mais_usados(df, periodo))
    secao("Prazo restante na aplicação", graficos.prazo_restante(df, periodo))
