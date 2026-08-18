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
      <p class="alert-title">{titulo}</p>
      <p class="muted">{texto}</p>
      <div class="alert-value">{valor}</div>
      <div class="alert-footer">
        <p class="kpi-label">{detalhe}</p>
        <span class="alert-dataset-slot"></span>
      </div>
    </div>
    """


def base_card(titulo: str, texto: str, status: str) -> str:
    """Card quadrado de uma base (SIM, Medicamentos…)."""
    return f"""
    <div class="glass-card base-card">
      <p class="topic-kicker">Base</p>
      <p class="base-card-title">{titulo}</p>
      <p class="muted">{texto}</p>
      <p class="topic-kicker">{status}</p>
    </div>
    """


def analise_card(titulo: str, texto: str, status: str) -> str:
    """Card de um tema da SIM (carrossel)."""
    return f"""
    <div class="glass-card analise-card">
      <p class="topic-kicker">Análise</p>
      <p class="base-card-title">{titulo}</p>
      <p class="muted">{texto}</p>
      <p class="topic-kicker">{status}</p>
    </div>
    """
