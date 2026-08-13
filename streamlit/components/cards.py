"""Cards HTML no visual glass do design."""


def kpi_card(titulo: str, valor: str, detalhe: str, chip: str, chip_class: str) -> str:
    """Card de indicador (número grande + chip de status)."""
    return f"""
    <div class="glass-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <p class="topic-kicker">{titulo}</p>
        <span class="chip {chip_class}">{chip}</span>
      </div>
      <div class="kpi-value">{valor}</div>
      <p class="kpi-label">{detalhe}</p>
    </div>
    """


def alert_card(kicker: str, titulo: str, texto: str, valor: str, detalhe: str) -> str:
    """Card de destaque (causa principal)."""
    return f"""
    <div class="alert-card">
      <p class="alert-kicker">{kicker}</p>
      <h2 style="font-family:'Hanken Grotesk',sans-serif;margin:0.2rem 0 0.5rem 0;">{titulo}</h2>
      <p class="muted">{texto}</p>
      <div class="alert-value">{valor}</div>
      <p class="kpi-label">{detalhe}</p>
    </div>
    """


def topic_card(fonte: str, titulo: str, texto: str, status: str) -> str:
    """Card de atalho para um tópico da SIM."""
    return f"""
    <div class="glass-card" style="min-height:160px;">
      <p class="topic-kicker">{fonte}</p>
      <h3 style="font-family:'Hanken Grotesk',sans-serif;margin:0.3rem 0;">{titulo}</h3>
      <p class="muted">{texto}</p>
      <p class="topic-kicker">{status}</p>
    </div>
    """
