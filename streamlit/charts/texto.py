"""Textos curtos abaixo dos gráficos."""


def insight_top(serie, extra: str = "") -> str:
    """Destaca a categoria mais frequente."""
    if serie is None or len(serie) == 0 or float(serie.sum()) == 0:
        return "Sem dados para este gráfico."
    nome = serie.idxmax()
    n = int(serie.max())
    pct = 100 * n / float(serie.sum())
    base = f'"{nome}" concentra {pct:.1f}% ({n}).'
    return f"{base} {extra}".strip()


def vazio(msg: str = "Sem dados para este gráfico."):
    """Par (figura, recado) quando não há o que plotar."""
    return None, msg
