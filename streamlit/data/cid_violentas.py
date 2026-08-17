"""Traduções CID usadas nas mortes violentas (notebook Sprint 1)."""

MAPA_CID_VIOLENTAS = {
    "V031": "Pedestre: colisão c/ carro (rua)",
    "V039": "Pedestre: colisão c/ carro (n/esp.)",
    "V041": "Pedestre: colisão c/ veículo pesado",
    "V099": "Pedestre: acidente trânsito n/esp.",
    "V134": "Ciclista: colisão c/ carro",
    "V139": "Ciclista: acidente trânsito n/esp.",
    "V199": "Motociclista: acidente n/esp.",
    "V234": "Motociclista: colisão c/ triciclo",
    "V244": "Motociclista: colisão c/ carro",
    "V274": "Motociclista: colisão c/ objeto fixo",
    "V299": "Motociclista: acidente trânsito n/esp.",
    "V445": "Ocup. carro: colisão (comércio)",
    "V446": "Ocup. carro: colisão (área industrial)",
    "V475": "Ocup. carro: colisão c/ objeto fixo",
    "V476": "Ocup. carro: colisão c/ objeto fixo (ind.)",
    "V499": "Ocup. carro: acidente n/esp.",
    "V892": "Acidente trânsito: veículo n/esp.",
    "V899": "Acidente trânsito n/esp.",
    "W190": "Queda não especificada",
    "W698": "Afogamento acidental",
    "W748": "Sufocação acidental",
    "W749": "Sufocação acidental n/esp.",
    "X599": "Exposição a fator acidental n/esp.",
    "X600": "Suicídio: envenenamento (residência)",
    "X640": "Suicídio: autointoxicação p/ drogas",
    "X700": "Suicídio: enforcamento (residência)",
    "X701": "Suicídio: enforcamento (hab. coletiva)",
    "X708": "Suicídio: enforcamento (outro local)",
    "X709": "Suicídio: enforcamento n/esp.",
    "X718": "Suicídio: afogamento (outro local)",
    "X740": "Suicídio: arma de fogo (residência)",
    "X748": "Suicídio: arma de fogo (outro local)",
    "X809": "Suicídio: precipitação (outro local)",
    "X930": "Homicídio: arma de fogo maior (residência)",
    "X934": "Homicídio: arma de fogo maior (rua/estrada)",
    "X935": "Homicídio: arma de fogo maior (comércio)",
    "X936": "Exposição a forças da natureza (área industrial)",
    "X938": "Homicídio: arma de fogo maior (outro local)",
    "X939": "Homicídio: arma de fogo maior (n/esp.)",
    "X950": "Homicídio: arma de fogo menor (residência)",
    "X954": "Homicídio: arma de fogo menor (rua/estrada)",
    "X959": "Homicídio: arma de fogo menor (n/esp.)",
    "X990": "Homicídio: objeto cortante (residência)",
    "X994": "Homicídio: objeto cortante (rua/estrada)",
    "X995": "Homicídio: objeto cortante (comércio)",
    "X999": "Homicídio: objeto cortante n/esp.",
    "Y000": "Homicídio: objeto contundente (residência)",
    "Y004": "Homicídio: objeto contundente (rua/estrada)",
    "Y09": "Homicídio: meio n/esp.",
    "Y349": "Evento de intenção indeterminada",
    "Y350": "Intervenção legal: arma de fogo",
    "R99": "Causa de morte desconhecida",
    "R960": "Morte súbita",
}


def traduz_cid_violenta(codigo) -> str:
    """Usa o mapa da sprint; se faltar, devolve o próprio código."""
    chave = str(codigo).strip().upper()
    return MAPA_CID_VIOLENTAS.get(chave, chave)


def tipo_violencia(cid) -> str:
    """Classifica causa externa em acidente, suicídio, homicídio ou outro."""
    texto = str(cid).strip().upper()
    if not texto:
        return "Outros/Indeterminado"
    if texto[0] in {"V", "W"} or _acidente_x(texto):
        return "Acidente"
    if _faixa_x(texto, 60, 84):
        return "Suicídio"
    if _faixa_x(texto, 85, 99) or texto.startswith("Y0"):
        return "Homicídio"
    return "Outros/Indeterminado"


def _acidente_x(cid: str) -> bool:
    """X00–X59 são acidentes na CID-10."""
    return _faixa_x(cid, 0, 59)


def _faixa_x(cid: str, inicio: int, fim: int) -> bool:
    """Indica se o código é X com os dois dígitos na faixa."""
    if not cid.startswith("X") or len(cid) < 3 or not cid[1:3].isdigit():
        return False
    return inicio <= int(cid[1:3]) <= fim
