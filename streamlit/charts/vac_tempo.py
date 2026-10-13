"""Gráficos: aplicações de vacinas ao longo do tempo."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.theme import PALETTE, PRIMARY, TERTIARY, apply_layout, bar_horizontal
from charts.texto import insight_top, vazio
from charts.vac_common import (
    com_data,
    linha_mensal_geral,
    linhas_por_grupo,
    mensal_contagem,
    serie_mensal_grupo,
)


def volume_mensal(df: pd.DataFrame, periodo: str):
    """Volume total de aplicações por mês."""
    mensal = mensal_contagem(df)
    return linha_mensal_geral(
        mensal, f"Quantidade de aplicações de vacinas por mês — {periodo}"
    )


def influenza_vs_outras(df: pd.DataFrame, periodo: str):
    """Compara influenza com as demais vacinas no tempo."""
    base = com_data(df)
    if base.empty:
        return vazio()
    base = base.assign(
        grupo=base["eh_influenza"].map({True: "Influenza trivalente", False: "Demais vacinas"})
    )
    tab = (
        base.groupby(["mes_periodo", "mes_label", "grupo"])
        .size()
        .reset_index(name="aplicacoes")
        .sort_values("mes_periodo")
    )
    fig = go.Figure()
    cores = {"Influenza trivalente": TERTIARY, "Demais vacinas": PRIMARY}
    for nome in ("Influenza trivalente", "Demais vacinas"):
        parte = tab.loc[tab["grupo"] == nome]
        fig.add_scatter(
            x=parte["mes_label"],
            y=parte["aplicacoes"],
            mode="lines+markers",
            name=nome,
            line=dict(color=cores[nome], width=3),
        )
    fig.update_yaxes(title="Número de aplicações", rangemode="tozero")
    fig.update_xaxes(title="Mês")
    fig.update_layout(legend_title_text="Grupo de vacina")
    # Insight do pico
    mensal = mensal_contagem(df)
    pico = mensal.loc[mensal["aplicacoes"].idxmax()]
    infl = int(
        tab.loc[
            (tab["mes_label"] == pico["mes_label"]) & (tab["grupo"] == "Influenza trivalente"),
            "aplicacoes",
        ].sum()
    )
    share = 100 * infl / pico["aplicacoes"] if pico["aplicacoes"] else 0
    insight = (
        f"No pico ({pico['mes_label']}), a influenza responde por {share:.1f}% "
        f"das aplicações — leitura de campanha, não de surto."
    )
    return apply_layout(fig, f"Influenza × demais vacinas — {periodo}"), insight


def top_vacinas_no_tempo(df: pd.DataFrame, periodo: str, n: int = 5):
    """Top N no tempo: com influenza e sem influenza (escala legível)."""
    col = _col_vacina(df)
    com = linhas_por_grupo(
        serie_mensal_grupo(df, col, top=n),
        col,
        f"Evolução mensal das {n} vacinas mais aplicadas — {periodo}",
        "Vacina",
    )
    sem_infl = df.loc[~df["eh_influenza"]] if "eh_influenza" in df.columns else df
    sem = linhas_por_grupo(
        serie_mensal_grupo(sem_infl, col, top=n),
        col,
        f"Top {n} sem influenza — {periodo}",
        "Vacina",
    )
    return [com, sem]


def _col_vacina(df: pd.DataFrame) -> str:
    """Prefere o nome curto quando a coluna existir."""
    return "vacina_curta" if "vacina_curta" in df.columns else "nome_da_vacina"


def vacinas_menos_frequentes(df: pd.DataFrame, periodo: str, limiar: int = 100):
    """Barras das vacinas raras, com nomes curtos e espaço para os números."""
    base = com_data(df)
    col = "vacina_curta" if "vacina_curta" in base.columns else "nome_da_vacina"
    serie = base[col].value_counts()
    baixa = serie[serie < limiar].sort_values(ascending=True)
    if baixa.empty:
        return vazio("Não há vacinas abaixo do limiar neste recorte.")
    plot = baixa.tail(15)
    fig = bar_horizontal(
        plot,
        f"Vacinas menos frequentes (< {limiar}) — {periodo}",
        mostrar_pct=False,
    )
    fig.update_xaxes(title="Número de aplicações")
    fig.update_traces(hovertemplate="%{y}<br>%{x} aplicações<extra></extra>")
    insight = _insight_menos_frequentes(plot.index, len(baixa), limiar)
    return fig, insight


_LEGENDA_CURTA = {
    "SCR": "sarampo, caxumba e rubéola",
    "SCR-V": "SCR + varicela",
    "VSR A e B": "vírus sincicial respiratório A e B",
    "VSR adjuvada": "vírus sincicial respiratório (adjuvada)",
    "Hexa": "DTPa / HepB / VIP / Hib",
    "Penta": "DTP / HepB / Hib",
    "Hib": "Haemophilus influenzae tipo b",
    "HPV": "papilomavírus humano",
}


def _insight_menos_frequentes(rotulos, n_total: int, limiar: int) -> str:
    """Texto do gráfico + legenda só das abreviações exibidas."""
    base = f"{n_total} vacina(s) com menos de {limiar} aplicações no período."
    itens = [f"{k} = {_LEGENDA_CURTA[k]}" for k in rotulos if k in _LEGENDA_CURTA]
    if not itens:
        return base
    return f"{base} Legenda: {'; '.join(itens)}."


def estrategias_no_tempo(df: pd.DataFrame, periodo: str, n: int = 4):
    """Evolução das principais estratégias."""
    tab = serie_mensal_grupo(df, "estrategia", top=n)
    return linhas_por_grupo(
        tab,
        "estrategia",
        f"Principais estratégias ao longo do tempo — {periodo}",
        "Estratégia",
    )


def bairros_no_tempo(df: pd.DataFrame, periodo: str, n: int = 5):
    """Evolução dos bairros com mais pessoas vacinadas."""
    tab = serie_mensal_grupo(df, "bairro", top=n)
    return linhas_por_grupo(
        tab,
        "bairro",
        f"Bairros com mais aplicações no tempo — {periodo}",
        "Bairro",
    )
