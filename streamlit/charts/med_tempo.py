"""Gráficos: dispensação ao longo do tempo."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from charts.texto import insight_top, vazio
from charts.theme import MUTED, PALETTE, PRIMARY, TERTIARY, abrevia, apply_layout
from data.prepare_med import mes_parcial

_LIMIAR_PCT = 8.0
_LIMIAR_Z = 2.0
_DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def volume_mensal_geral(df: pd.DataFrame, periodo: str):
    """Linha mensal bruta com mês parcial em marcador vazado."""
    mensal = _serie_mensal(df, metodo="bruto")
    if mensal.empty:
        return vazio()
    fig = apply_layout(_linha_mensal(mensal, PRIMARY, "Rede"), f"Quantidade total por mês — {periodo}")
    fig.update_yaxes(title="Quantidade")
    n = int(mensal["relevante"].sum())
    insight = f"{n} mês(es) com variação ≥ {_LIMIAR_PCT:.0f}%." if n else "Variações mensais dentro de ±8%."
    return fig, insight


def tendencia_mensal_coluna(
    df: pd.DataFrame, coluna: str, periodo: str, n: int = 5, metodo: str = "indice"
):
    """Multi-linha mensal dos top-N grupos por quantidade."""
    ranking = _top_grupos(df, coluna, n)
    if ranking.empty:
        return vazio()
    fig = go.Figure()
    for i, nome in enumerate(ranking):
        mensal = _serie_mensal(df.loc[df[coluna] == nome], metodo=metodo)
        _linha_mensal(mensal, PALETTE[i % len(PALETTE)], abrevia(str(nome), 24), fig=fig)
    titulo = f"Tendência mensal — top {len(ranking)} {coluna.replace('_', ' ')} · {periodo}"
    return _com_legenda_baixo(apply_layout(fig, titulo)), insight_top(_totais(df, coluna).head(n))


def top5_classes_linha(df: pd.DataFrame, periodo: str):
    """Top 5 classes terapêuticas só em meses completos."""
    base = df.loc[~df["eh_mes_parcial"]]
    if base.empty:
        return vazio()
    top5 = _totais(base, "classe_terapeutica").head(5)
    fig = go.Figure()
    for i, nome in enumerate(top5.index):
        mensal = base.loc[base["classe_terapeutica"] == nome].groupby("ano_mes")["quantidade"].sum()
        fig.add_scatter(
            x=mensal.index.astype(str),
            y=mensal.values,
            mode="lines+markers",
            name=abrevia(str(nome), 24),
            line=dict(color=PALETTE[i % len(PALETTE)], width=2),
        )
    fig = apply_layout(fig, f"Top 5 classes terapêuticas (meses completos) — {periodo}")
    return _com_legenda_baixo(fig), insight_top(top5)


def padrao_diario_rede(df: pd.DataFrame, periodo: str):
    """Série diária (dias úteis) + padrão semanal + anomalias."""
    diario = _serie_diaria(df)
    if diario.empty:
        return vazio()
    fig = _canvas_diario()
    _tracos_uteis(fig, diario.loc[diario["dia_semana"] < 5])
    anom, fer = _marcar_anomalias(fig, diario)
    _sombrear_parcial(fig, df, diario)
    padrao = _traco_semanal(fig, diario)
    fig = apply_layout(fig, f"Padrão diário da rede — {periodo}")
    fig.update_layout(height=560, legend=dict(orientation="h", y=-0.08))
    uteis = padrao.iloc[:5]
    insight = (
        f"Entre dias úteis, pico em {_DIAS[int(uteis.idxmax())]} "
        f"e vale em {_DIAS[int(uteis.idxmin())]}. "
        f"{len(anom)} anomalia(s), {len(fer)} possível(is) feriado(s)."
    )
    return fig, insight


def tabela_resumo_bairro(df: pd.DataFrame) -> pd.DataFrame:
    """Ranking de bairros por quantidade + participação %."""
    base = df.loc[~df["bairro_malformado"]]
    total = base["quantidade"].sum() or 1
    resumo = (
        base.groupby("bairro_padronizado")["quantidade"].sum().sort_values(ascending=False).reset_index()
    )
    resumo.columns = ["Bairro", "Total"]
    resumo["Participação %"] = (resumo["Total"] / total * 100).round(2)
    resumo.insert(0, "Ranking", range(1, len(resumo) + 1))
    return resumo


def tabelas_anomalias(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabelas de anomalias de volume e possíveis feriados."""
    diario = _serie_diaria(df)
    anom = diario.loc[diario["anomalia"] & ~diario["feriado"], ["data", "quantidade_bruta", "z_score"]]
    fer = diario.loc[diario["anomalia"] & diario["feriado"], ["data", "quantidade_bruta"]]
    anom = anom.assign(
        data=anom["data"].dt.strftime("%d/%m/%Y"),
        quantidade_bruta=anom["quantidade_bruta"].round(0),
        z_score=anom["z_score"].round(2),
    ).rename(columns={"data": "Data", "quantidade_bruta": "Qtd", "z_score": "z"})
    fer = fer.assign(data=fer["data"].dt.strftime("%d/%m/%Y")).rename(
        columns={"data": "Data", "quantidade_bruta": "Qtd"}
    )
    return anom.reset_index(drop=True), fer.reset_index(drop=True)


def _serie_mensal(df: pd.DataFrame, metodo: str = "bruto") -> pd.DataFrame:
    """Agrega quantidade por mês e marca parcial / variação relevante."""
    parcial = mes_parcial(df)
    mensal = df.groupby("ano_mes", as_index=False)["quantidade"].sum().sort_values("ano_mes")
    mensal["parcial"] = mensal["ano_mes"] == parcial if parcial else False
    mensal["quantidade_bruta"] = mensal["quantidade"]
    media = mensal.loc[~mensal["parcial"], "quantidade_bruta"].mean() or 0
    if metodo == "indice" and media:
        mensal["quantidade"] = mensal["quantidade_bruta"] / media * 100
    mensal["variacao_pct"] = mensal["quantidade_bruta"].pct_change() * 100
    mensal["relevante"] = (mensal["variacao_pct"].abs() >= _LIMIAR_PCT) & (~mensal["parcial"])
    return mensal


def _linha_mensal(mensal, cor, nome, fig=None) -> go.Figure:
    """Desenha meses completos + parcial (vazado / tracejado)."""
    fig = fig or go.Figure()
    completos = mensal.loc[~mensal["parcial"]]
    parcial = mensal.loc[mensal["parcial"]]
    fig.add_scatter(
        x=completos["ano_mes"],
        y=completos["quantidade"],
        mode="lines+markers",
        name=nome,
        line=dict(color=cor, width=2.2),
        marker=dict(size=7, color=cor, line=dict(color="white", width=1)),
    )
    _anotar_variacoes(fig, completos)
    _ligar_parcial(fig, completos, parcial, cor)
    return fig


def _anotar_variacoes(fig: go.Figure, completos: pd.DataFrame) -> None:
    """Rótulos Δ% nos meses com variação relevante."""
    for _, row in completos.loc[completos["relevante"]].iterrows():
        fig.add_annotation(
            x=row["ano_mes"],
            y=row["quantidade"],
            text=f"{row['variacao_pct']:+.0f}%",
            showarrow=False,
            yshift=14,
            font=dict(size=10, color=TERTIARY if row["variacao_pct"] < 0 else "#2ca02c"),
        )


def _ligar_parcial(fig, completos, parcial, cor) -> None:
    """Liga o último mês completo ao parcial com linha tracejada."""
    if parcial.empty or completos.empty:
        return
    fig.add_scatter(
        x=list(completos["ano_mes"].tail(1)) + list(parcial["ano_mes"]),
        y=list(completos["quantidade"].tail(1)) + list(parcial["quantidade"]),
        mode="lines",
        line=dict(color=cor, width=1.6, dash="dash"),
        showlegend=False,
        opacity=0.55,
    )
    fig.add_scatter(
        x=parcial["ano_mes"],
        y=parcial["quantidade"],
        mode="markers",
        marker=dict(size=9, color="white", line=dict(color=cor, width=2)),
        showlegend=False,
    )


def _serie_diaria(df: pd.DataFrame) -> pd.DataFrame:
    """Série diária com z-score (janela 10 dias úteis)."""
    parcial = mes_parcial(df)
    diario = df.groupby("data")["quantidade"].sum().asfreq("D").fillna(0).reset_index()
    diario.columns = ["data", "quantidade_bruta"]
    diario["dia_semana"] = diario["data"].dt.dayofweek
    diario["parcial"] = diario["data"].dt.to_period("M").astype(str) == parcial if parcial else False
    uteis = diario.loc[(diario["dia_semana"] < 5) & (~diario["parcial"])].copy()
    uteis["media_movel"] = uteis["quantidade_bruta"].rolling(10, min_periods=5, center=True).mean()
    uteis["std_movel"] = uteis["quantidade_bruta"].rolling(10, min_periods=5, center=True).std()
    uteis["z_score"] = (uteis["quantidade_bruta"] - uteis["media_movel"]) / uteis["std_movel"]
    uteis["anomalia"] = uteis["z_score"].abs() >= _LIMIAR_Z
    uteis["feriado"] = uteis["quantidade_bruta"] == 0
    diario = diario.merge(uteis[["data", "media_movel", "z_score", "anomalia", "feriado"]], on="data", how="left")
    diario["anomalia"] = diario["anomalia"].fillna(False)
    diario["feriado"] = diario["feriado"].fillna(False)
    return diario


def _canvas_diario() -> go.Figure:
    """Dois painéis: tendência diária + padrão semanal."""
    return make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.68, 0.32],
        vertical_spacing=0.12,
        subplot_titles=("Dias úteis — tendência e anomalias", "Padrão por dia da semana"),
    )


def _tracos_uteis(fig: go.Figure, uteis: pd.DataFrame) -> None:
    """Linha diária + média móvel no painel superior."""
    fig.add_scatter(
        x=uteis["data"], y=uteis["quantidade_bruta"], mode="lines", name="Volume",
        line=dict(color=PRIMARY, width=1), opacity=0.45, row=1, col=1,
    )
    fig.add_scatter(
        x=uteis["data"], y=uteis["media_movel"], mode="lines", name="Média móvel (10 dias)",
        line=dict(color=PRIMARY, width=2.2), row=1, col=1,
    )


def _marcar_anomalias(fig: go.Figure, diario: pd.DataFrame):
    """Marca anomalias de volume e possíveis feriados."""
    anom = diario.loc[diario["anomalia"] & ~diario["feriado"]]
    fer = diario.loc[diario["anomalia"] & diario["feriado"]]
    fig.add_scatter(
        x=anom["data"], y=anom["quantidade_bruta"], mode="markers", name="Anomalia (|z|≥2)",
        marker=dict(color=TERTIARY, size=9, line=dict(color="white", width=1)), row=1, col=1,
    )
    fig.add_scatter(
        x=fer["data"], y=fer["quantidade_bruta"], mode="markers", name="Provável feriado",
        marker=dict(symbol="x", color=MUTED, size=9, line=dict(width=2)), row=1, col=1,
    )
    return anom, fer


def _sombrear_parcial(fig: go.Figure, df: pd.DataFrame, diario: pd.DataFrame) -> None:
    """Área cinza no mês parcial."""
    parcial = mes_parcial(df)
    if not parcial:
        return
    fig.add_vrect(
        x0=pd.Period(parcial).start_time, x1=diario["data"].max(),
        fillcolor="gray", opacity=0.08, line_width=0, row=1, col=1,
    )


def _traco_semanal(fig: go.Figure, diario: pd.DataFrame) -> pd.Series:
    """Média e faixa de desvio por dia da semana."""
    base = diario.loc[~diario["parcial"]]
    padrao = base.groupby("dia_semana")["quantidade_bruta"].mean().reindex(range(7))
    desvio = base.groupby("dia_semana")["quantidade_bruta"].std().reindex(range(7)).fillna(0)
    fig.add_scatter(
        x=_DIAS, y=padrao.values, mode="lines+markers", name="Média semanal",
        line=dict(color=PRIMARY, width=2), row=2, col=1,
    )
    fig.add_scatter(x=_DIAS, y=(padrao - desvio).values, mode="lines", line=dict(width=0), showlegend=False, row=2, col=1)
    fig.add_scatter(
        x=_DIAS, y=(padrao + desvio).values, mode="lines", fill="tonexty",
        fillcolor="rgba(0,89,187,0.12)", line=dict(width=0), showlegend=False, row=2, col=1,
    )
    return padrao


def _com_legenda_baixo(fig: go.Figure) -> go.Figure:
    """Legenda horizontal abaixo do gráfico."""
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="center", x=0.5),
        margin=dict(l=8, r=8, t=56, b=100),
    )
    return fig


def _totais(df: pd.DataFrame, coluna: str) -> pd.Series:
    """Soma de quantidade por grupo."""
    return df.groupby(coluna)["quantidade"].sum().sort_values(ascending=False)


def _top_grupos(df: pd.DataFrame, coluna: str, n: int) -> pd.Index:
    """Índice dos n grupos com maior quantidade."""
    return _totais(df, coluna).head(n).index
