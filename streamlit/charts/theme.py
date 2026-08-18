"""Tema Plotly alinhado à paleta de Araranguá."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from data.constants import rotulo_coluna

PRIMARY = "#0059bb"
SECONDARY = "#fdc003"
TERTIARY = "#b6152e"
MUTED = "#717786"
PALETTE = [PRIMARY, TERTIARY, SECONDARY, "#004493", "#d93343", "#fabd00"]

_TEXTO_CLARO = "#191c1d"
_TEXTO_ESCURO = "#e8eaed"
_GRADE_CLARA = "#e1e3e4"
_GRADE_ESCURA = "#2c333d"


def _escuro() -> bool:
    """Indica se o portal está no tema escuro."""
    return bool(st.session_state.get("tema_escuro"))


def apply_layout(fig: go.Figure, title: str) -> go.Figure:
    """Aplica fundo limpo, fonte Inter e título."""
    texto = _TEXTO_ESCURO if _escuro() else _TEXTO_CLARO
    grade = _GRADE_ESCURA if _escuro() else _GRADE_CLARA
    fig.update_layout(
        title=title,
        font=dict(family="Inter, sans-serif", color=texto, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=56, b=8),
        title_font=dict(family="Hanken Grotesk, sans-serif", size=18, color=texto),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=texto)),
        coloraxis_colorbar=dict(tickfont=dict(color=texto), title_font=dict(color=texto)),
    )
    fig.update_xaxes(
        showgrid=False, color=texto,
        tickfont=dict(color=texto), title_font=dict(color=texto),
    )
    fig.update_yaxes(
        gridcolor=grade, zeroline=False, color=texto,
        tickfont=dict(color=texto), title_font=dict(color=texto),
    )
    _titulos_eixo_legiveis(fig)
    return fig


def _texto_eixo(eixo) -> str:
    """Lê o título atual de um eixo ou da legenda Plotly."""
    titulo = getattr(eixo, "title", None) if eixo is not None else None
    texto = getattr(titulo, "text", None) if titulo is not None else None
    return str(texto) if texto else ""


def _titulos_eixo_legiveis(fig: go.Figure) -> None:
    """Troca FAIXA_ETARIA e similares por rótulo em português."""
    fig.update_xaxes(title=rotulo_coluna(_texto_eixo(fig.layout.xaxis)))
    fig.update_yaxes(title=rotulo_coluna(_texto_eixo(fig.layout.yaxis)))
    legenda = _texto_eixo(fig.layout.legend)
    if legenda:
        fig.update_layout(legend_title_text=rotulo_coluna(legenda))


def tem_heatmap(fig: go.Figure) -> bool:
    """Indica se a figura é um mapa de calor."""
    return any(getattr(t, "type", "") == "heatmap" for t in fig.data)


def tema_plotly(fig: go.Figure) -> str | None:
    """Heatmap não usa o tema Streamlit (ele força letra branca nas células)."""
    return None if tem_heatmap(fig) else "streamlit"


def adaptar_tema(fig: go.Figure) -> go.Figure:
    """Ajusta cores do gráfico ao tema atual (claro/escuro)."""
    if not _escuro():
        return fig
    texto = _TEXTO_ESCURO
    grade = _GRADE_ESCURA
    fig.update_layout(
        font=dict(color=texto),
        title_font=dict(color=texto),
        legend=dict(font=dict(color=texto)),
        coloraxis_colorbar=dict(tickfont=dict(color=texto), title_font=dict(color=texto)),
    )
    fig.update_xaxes(color=texto, tickfont=dict(color=texto), title_font=dict(color=texto))
    fig.update_yaxes(color=texto, tickfont=dict(color=texto), gridcolor=grade, title_font=dict(color=texto))
    if not tem_heatmap(fig):
        fig.update_annotations(font=dict(color=texto))
    fig.update_traces(textfont=dict(color=texto), selector=dict(type="bar"))
    return fig


def rotulo(valor: float, total: float, mostrar_pct: bool) -> str:
    """Texto da barra: n ou n (pct%)."""
    if mostrar_pct and total:
        return f"{int(valor)} ({100 * valor / total:.1f}%)"
    return f"{int(valor)}" if valor == int(valor) else f"{valor:.1f}"


def bar_vertical(serie, title: str, mostrar_pct: bool = True, color: str = PRIMARY):
    """Gráfico de barras verticais com rótulo."""
    total = float(serie.sum()) if len(serie) else 0
    textos = [rotulo(v, total, mostrar_pct) for v in serie.values]
    fig = go.Figure(
        go.Bar(
            x=[str(i) for i in serie.index],
            y=list(serie.values),
            text=textos,
            textposition="outside",
            marker_color=color,
            cliponaxis=False,
        )
    )
    return apply_layout(fig, title)


def bar_horizontal(serie, title: str, mostrar_pct: bool = True, cores=None):
    """Gráfico de barras horizontais (maior no topo)."""
    total = float(serie.sum()) if len(serie) else 0
    textos = [rotulo(v, total, mostrar_pct) for v in serie.values]
    fig = go.Figure(
        go.Bar(
            y=[str(i) for i in serie.index],
            x=list(serie.values),
            orientation="h",
            text=textos,
            textposition="outside",
            marker_color=cores or PRIMARY,
            cliponaxis=False,
        )
    )
    fig.update_yaxes(autorange="reversed")
    return apply_layout(fig, title)


def barras_empilhadas(tabela, title: str, horizontal: bool = False, cores=None):
    """Barras empilhadas a partir de uma tabela (index × colunas)."""
    fig = go.Figure()
    paleta = cores or PALETTE
    for i, col in enumerate(tabela.columns):
        kwargs = _barra_empilhada(tabela, col, paleta[i % len(paleta)], horizontal)
        fig.add_bar(**kwargs)
    fig.update_layout(barmode="stack")
    if horizontal:
        fig.update_yaxes(autorange="reversed")
    return apply_layout(fig, title)


def _barra_empilhada(tabela, col, cor: str, horizontal: bool) -> dict:
    """Uma camada do empilhamento."""
    eixo = [str(i) for i in tabela.index]
    valores = list(tabela[col])
    if horizontal:
        return dict(y=eixo, x=valores, orientation="h", name=str(col), marker_color=cor)
    return dict(x=eixo, y=valores, name=str(col), marker_color=cor)


def barras_agrupadas(tabela, title: str, horizontal: bool = False):
    """Barras lado a lado (ex.: Araranguá × Tubarão × SC)."""
    fig = go.Figure()
    for i, col in enumerate(tabela.columns):
        kwargs = _barra_empilhada(tabela, col, PALETTE[i % len(PALETTE)], horizontal)
        fig.add_bar(**kwargs)
    fig.update_layout(barmode="group")
    if horizontal:
        fig.update_yaxes(autorange="reversed")
    return apply_layout(fig, title)


def boxplot(grupos: dict, title: str) -> go.Figure:
    """Caixas sem outliers, uma por categoria."""
    fig = go.Figure()
    for i, (nome, valores) in enumerate(grupos.items()):
        fig.add_box(
            y=list(valores),
            name=str(nome),
            marker_color=PALETTE[i % len(PALETTE)],
            boxpoints=False,
        )
    return apply_layout(fig, title)


def histograma(valores, title: str, nbins: int = 10, color: str = PRIMARY) -> go.Figure:
    """Histograma simples."""
    fig = go.Figure(go.Histogram(x=list(valores), nbinsx=nbins, marker_color=color))
    return apply_layout(fig, title)


def histograma_hue(df, x: str, hue: str, title: str, nbins: int = 10) -> go.Figure:
    """Histograma colorido por categoria."""
    fig = px.histogram(
        df, x=x, color=hue, nbins=nbins, barmode="group",
        color_discrete_sequence=PALETTE,
    )
    return apply_layout(fig, title)


def linha(serie, title: str) -> go.Figure:
    """Série em linha com marcadores."""
    fig = go.Figure(
        go.Scatter(
            x=[str(i) for i in serie.index],
            y=list(serie.values),
            mode="lines+markers",
            line=dict(color=PRIMARY),
        )
    )
    return apply_layout(fig, title)


def dispersao(x, y, title: str, xlabel: str = "", ylabel: str = "") -> go.Figure:
    """Nuvem de pontos."""
    fig = go.Figure(
        go.Scatter(
            x=list(x),
            y=list(y),
            mode="markers",
            marker=dict(color=PRIMARY, opacity=0.55, size=8),
        )
    )
    fig.update_xaxes(title=xlabel)
    fig.update_yaxes(title=ylabel)
    return apply_layout(fig, title)


def bolhas_geo(geo, title: str) -> go.Figure:
    """Mapa de bolhas (longitude × latitude)."""
    fig = go.Figure(
        go.Scatter(
            x=geo["lon"], y=geo["lat"], mode="markers+text",
            text=_rotulos_geo(geo), textposition="top center",
            marker=_marcador_bolha(geo),
            hovertext=geo["nome"] + "<br>" + geo["obitos"].astype(int).astype(str),
            hoverinfo="text",
        )
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1, title="Latitude")
    fig.update_xaxes(title="Longitude")
    return apply_layout(fig, title)


def _marcador_bolha(geo) -> dict:
    """Tamanho proporcional à raiz do volume de óbitos."""
    tamanho = (geo["obitos"] ** 0.5) / (geo["obitos"].max() ** 0.5) * 40 + 6
    return dict(size=tamanho, color=geo["obitos"], colorscale="YlOrRd", showscale=True, opacity=0.75)


def _rotulos_geo(geo) -> list[str]:
    """Nome só nos 10 municípios com mais óbitos."""
    top = set(geo.head(10)["nome"])
    return [n if n in top else "" for n in geo["nome"]]


def heatmap(tabela, title: str, escala: str = "Blues") -> go.Figure:
    """Heatmap com números contrastantes (escuro em célula clara)."""
    eixo_x = rotulo_coluna(tabela.columns.name)
    eixo_y = rotulo_coluna(tabela.index.name)
    dados = _tabela_heatmap(tabela)
    fig = px.imshow(
        dados,
        color_continuous_scale=escala,
        aspect="auto",
        text_auto=False,
        template=None,
        labels=dict(x=eixo_x, y=eixo_y, color="Óbitos"),
    )
    _rotulos_heatmap(fig, dados)
    fig = apply_layout(fig, title)
    _encaixar_heatmap(fig, eixo_x, eixo_y, len(dados.index))
    return fig


def _tabela_heatmap(tabela):
    """Copia sem nome de coluna cru (FAIXA_ETARIA) nos eixos."""
    dados = tabela.copy()
    dados.index = dados.index.astype(str)
    dados.columns = dados.columns.astype(str)
    dados.index.name = None
    dados.columns.name = None
    return dados


def _encaixar_heatmap(fig: go.Figure, eixo_x: str, eixo_y: str, n_linhas: int) -> None:
    """Abre margem dos rótulos e trava o zoom."""
    fig.update_layout(
        margin=dict(l=96, r=72, t=56, b=72),
        dragmode=False,
        height=max(360, min(520, 56 * n_linhas + 140)),
        coloraxis_colorbar=dict(title="Óbitos"),
    )
    fig.update_xaxes(
        title=eixo_x, automargin=True, fixedrange=True, tickangle=0, ticks="outside",
    )
    fig.update_yaxes(
        title=eixo_y, automargin=True, fixedrange=True, ticks="outside",
    )


def _cor_rotulo_celula(valor: float, vmax: float) -> str:
    """Branco em célula escura; preto em célula clara."""
    if vmax <= 0 or valor / vmax < 0.45:
        return _TEXTO_CLARO
    return "#ffffff"


def _rotulos_heatmap(fig: go.Figure, tabela) -> None:
    """Número em cada célula, com cor que contrasta o fundo."""
    vmax = float(tabela.max().max()) if not tabela.empty else 0
    rotulos = []
    for y in tabela.index:
        for x in tabela.columns:
            valor = float(tabela.loc[y, x])
            rotulos.append(
                dict(
                    x=str(x),
                    y=str(y),
                    text=f"{valor:.0f}",
                    showarrow=False,
                    xref="x",
                    yref="y",
                    font=dict(color=_cor_rotulo_celula(valor, vmax), size=12),
                )
            )
    fig.update_layout(annotations=rotulos)


def abrevia(texto: str, tamanho: int = 35) -> str:
    """Corta rótulos longos para caber no eixo."""
    texto = str(texto)
    if len(texto) <= tamanho:
        return texto
    return texto[: tamanho - 1].rstrip() + "…"
