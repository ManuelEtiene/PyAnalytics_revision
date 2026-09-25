"""Gráfico da busca: lugar × quantidade."""

from charts.texto import insight_top, vazio
from charts.theme import abrevia, bar_horizontal

_TOP_GRAFICO = 15


def quantidade_por_lugar(tabela, medicamento: str, mes: str):
    """Barras de quantidade por lugar no último mês."""
    if tabela.empty:
        return vazio("Sem dispensação deste medicamento no último mês.")
    plot = tabela.set_index("Lugar")["Quantidade"].head(_TOP_GRAFICO)
    plot.index = [abrevia(i, 28) for i in plot.index]
    fig = bar_horizontal(
        plot, f"Quantidade por lugar — {medicamento} · {mes}", mostrar_pct=False
    )
    return fig, insight_top(plot, "Volume maior no lugar que mais retirou o item.")
