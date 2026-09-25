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


def base_card(titulo: str, texto: str, status: str, pronto: bool = True) -> str:
    """Card quadrado de uma base (SIM, Medicamentos…)."""
    chip = "chip-yellow" if pronto else "chip-blue"
    return f"""
    <div class="glass-card base-card">
      <div class="analise-card-topo">
        <p class="topic-kicker">Base</p>
        <span class="chip {chip}">{status}</span>
      </div>
      <p class="base-card-title">{titulo}</p>
      <p class="muted">{texto}</p>
    </div>
    """


def analise_card(
    titulo: str,
    texto: str,
    status: str,
    pronto: bool = True,
    kicker: str = "Análise",
) -> str:
    """Card de um tema da base (hub SIM / Medicamentos / Vacinações)."""
    chip = "chip-yellow" if pronto else "chip-blue"
    return f"""
    <div class="glass-card analise-card">
      <div class="analise-card-topo">
        <p class="topic-kicker analise-kicker">{kicker}</p>
        <span class="chip {chip}">{status}</span>
      </div>
      <p class="base-card-title">{titulo}</p>
      <p class="muted">{texto}</p>
    </div>
    """
