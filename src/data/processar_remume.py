"""Extrai a REMUME (PDF) para CSV organizado por categoria e local."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import fitz
import pandas as pd

# Colunas do PDF (coordenada X aproximada).
_X_ITEM = 105
_X_MED = 195
_X_APRES = 400

_LIXO = {
    "item",
    "ite",
    "m",
    "medicamento",
    "medicamen",
    "to",
    "apresentação",
    "apresentacao",
    "local",
    "de",
    "acesso",
    "local de",
    "local de acesso",
}

# Ordem = aparição no PDF.
CATEGORIAS = (
    "Analgésicos",
    "Antibacterianos",
    "Antivirais",
    "Antifúngicos",
    "Antiglaucomatosos",
    "Antigotosos",
    "Antihistamínicos",
    "Anti-inflamatórios",
    "Antiparasitários",
    "Corticosteróides",
    "Hipolipemiantes",
    "Hormônio Tireoidiano",
    "Insulinas e Antidiabéticos Orais",
    "Laxativos",
    "Medicamentos que Atuam sobre o Sistema Cardiovascular",
    "Medicamentos que Atuam sobre o Sistema Digestivo",
    "Medicamentos que Atuam sobre o Sistema Nervoso Central",
    "Medicamentos que Atuam sobre o Sistema Respiratório",
    "Medicamentos e Produtos que Atuam no Sistema Reprodutor",
    "Medicamentos Utilizado no Tratamento/Prevenção de Osteoporose",
    "Vitaminas e Sais Minerais",
    "Fitoterápicos",
    "Outros",
)

_RE_DOSE = re.compile(
    r"\d|mg|ml|mcg|g\b|%|ui\b|comprimid|capsul|cápsul|soluç|suspens|xarope|"
    r"creme|gel|loç|pomada|ampola|frasco|inala|injet",
    re.I,
)

UBS_BAIRROS = (
    "Hercílio Luz",
    "Morro dos Conventos",
    "Jardim das Avenidas",
    "Coloninha",
    "Urussanguinha",
    "Vila São José",
    "Cidade Alta",
    "Divinéia",
    "Mato Alto",
    "Lagoão",
    "Jardim Cibele",
    "Polícia Rodoviária",
    "Sanga da Areia",
    "Sanga da Toca",
)

FARMACIA_REF = "Farmácia Bom Pastor"


def processar(pdf: Path, saida: Path) -> pd.DataFrame:
    """Lê o PDF, organiza itens e grava o CSV."""
    palavras = _ler_palavras(pdf)
    linhas = _agrupar_linhas(palavras)
    itens = _montar_itens(linhas)
    df = _enriquecer(pd.DataFrame(itens))
    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(saida, index=False)
    return df


def _ler_palavras(pdf: Path) -> list[tuple[float, float, str]]:
    """Palavras com (x, y global, texto)."""
    doc = fitz.open(pdf)
    palavras: list[tuple[float, float, str]] = []
    y_off = 0.0
    for page in doc:
        for x0, y0, _x1, _y1, text, *_ in page.get_text("words"):
            t = text.strip()
            if t:
                palavras.append((float(x0), float(y0) + y_off, t))
        y_off += page.rect.height + 40
    return palavras


def _agrupar_linhas(
    palavras: list[tuple[float, float, str]], tol: float = 4.0
) -> list[list[tuple[float, float, str]]]:
    """Agrupa palavras na mesma linha visual."""
    ordenadas = sorted(palavras, key=lambda p: (round(p[1] / tol), p[0]))
    linhas: list[list[tuple[float, float, str]]] = []
    atual: list[tuple[float, float, str]] = []
    y_ref: float | None = None
    for p in ordenadas:
        if y_ref is None or abs(p[1] - y_ref) <= tol:
            atual.append(p)
            y_ref = p[1] if y_ref is None else y_ref
            continue
        linhas.append(sorted(atual, key=lambda t: t[0]))
        atual = [p]
        y_ref = p[1]
    if atual:
        linhas.append(sorted(atual, key=lambda t: t[0]))
    return linhas


def _montar_itens(linhas: list[list[tuple[float, float, str]]]) -> list[dict]:
    """Monta registros item / medicamento / apresentação / local."""
    categoria = ""
    buf_cat: list[str] = []
    atual: dict | None = None
    itens: list[dict] = []

    for linha in linhas:
        texto = _limpar(" ".join(p[2] for p in linha))
        cat = _detectar_categoria(texto, buf_cat)
        if cat:
            categoria = cat
            buf_cat.clear()
            continue
        if _eh_cabecalho(texto):
            continue

        num = _numero_item(linha)
        cols = _colunas(linha)
        if num is not None:
            if atual and atual.get("item") is None:
                atual["item"] = num
                _acrescentar(atual, cols)
            else:
                if atual:
                    itens.append(atual)
                atual = _novo(num, categoria, cols)
            continue

        if atual is None:
            continue

        # Nome desalinhado acima do número (ex.: item 28).
        if _item_completo(atual) and _parece_novo(cols):
            itens.append(atual)
            atual = _novo(None, categoria, cols)
            continue

        _acrescentar(atual, cols)

    if atual:
        itens.append(atual)
    return [i for i in itens if i.get("medicamento")]


def _detectar_categoria(texto: str, buf: list[str]) -> str | None:
    """Casa categoria completa ou acumula título multilinha."""
    if not texto or _eh_cabecalho(texto) or re.match(r"^\d", texto):
        return None

    def _casa(chave: str) -> str | None:
        for cat in CATEGORIAS:
            nc = _norm(cat)
            if chave == nc or chave.startswith(nc) or nc.startswith(chave):
                # Evita casar "Medicamentos que..." cedo demais.
                if nc.startswith("medicamentos") and len(chave) < 28:
                    continue
                if abs(len(chave) - len(nc)) <= 24 or chave.startswith(nc):
                    return cat
        return None

    # Completa título acumulado (ex.: "... DE" + "OSTEOPOROSE").
    if buf:
        buf.append(texto)
        achado = _casa(_norm(_limpar(" ".join(buf))))
        if achado:
            buf.clear()
            return achado
        if len(buf) > 4:
            buf.clear()
        return None

    direto = _casa(_norm(texto))
    if direto and _norm(texto) == _norm(direto):
        return direto

    if _parece_titulo(texto):
        buf.append(texto)
        achado = _casa(_norm(_limpar(" ".join(buf))))
        if achado and len(_norm(" ".join(buf))) >= min(18, len(_norm(achado)) - 5):
            buf.clear()
            return achado
        return None

    return direto if direto and len(_norm(texto)) >= 6 else None


def _parece_titulo(texto: str) -> bool:
    """Linha candidata a título de seção do REMUME."""
    n = _norm(texto)
    if n in {"osteoporose"}:
        return True
    return any(
        n.startswith(_norm(p))
        for p in (
            "Medicamentos que",
            "Medicamentos e",
            "Medicamentos utilizado",
            "Insulinas e",
            "Hormônio",
            "Vitaminas e",
            "Anti-",
            "Analgésicos",
            "Antibacterianos",
            "Antivirais",
            "Antifúngicos",
            "Antiglaucomatosos",
            "Antigotosos",
            "Antihistamínicos",
            "Antiparasitários",
            "Corticosteróides",
            "Hipolipemiantes",
            "Laxativos",
            "Fitoterápicos",
            "Outros",
        )
    )


def _eh_cabecalho(texto: str) -> bool:
    """Linha de cabeçalho da tabela do PDF."""
    n = _norm(texto)
    if not n:
        return True
    if n in _LIXO:
        return True
    return any(
        p in n
        for p in (
            "item medicamen",
            "apresentacao local",
            "local de acesso",
            "medicamen to",
        )
    )


def _numero_item(linha: list[tuple[float, float, str]]) -> int | None:
    """Detecta início de item (ex.: '12.' ou '149' + '.')."""
    esq = [p for p in linha if p[0] < _X_ITEM]
    if not esq:
        return None
    juntado = "".join(p[2] for p in esq)
    m = re.match(r"^(\d+)\.+?$", juntado)
    if m:
        return int(m.group(1))
    if len(esq) >= 2 and esq[0][2].isdigit() and esq[1][2].startswith("."):
        return int(esq[0][2])
    m = re.match(r"^(\d+)\.?$", esq[0][2])
    return int(m.group(1)) if m else None


def _colunas(linha: list[tuple[float, float, str]]) -> dict[str, str]:
    """Separa medicamento / apresentação / local pela posição X."""
    med, apres, local = [], [], []
    for x, _y, t in linha:
        if x < _X_ITEM:
            continue
        if x < _X_MED:
            med.append(t)
        elif x < _X_APRES:
            apres.append(t)
        else:
            local.append(t)
    return {
        "medicamento": _limpar_campo(" ".join(med)),
        "apresentacao": _limpar_campo(" ".join(apres)),
        "local": _limpar_campo(" ".join(local)),
    }


def _novo(num: int | None, categoria: str, cols: dict) -> dict:
    return {
        "item": num,
        "categoria": categoria,
        "medicamento": cols["medicamento"],
        "apresentacao": cols["apresentacao"],
        "local_bruto": cols["local"],
    }


def _acrescentar(atual: dict, cols: dict) -> None:
    for chave, origem in (
        ("medicamento", "medicamento"),
        ("apresentacao", "apresentacao"),
        ("local_bruto", "local"),
    ):
        if cols[origem]:
            atual[chave] = _limpar(f"{atual.get(chave, '')} {cols[origem]}")


def _item_completo(atual: dict) -> bool:
    return bool(atual.get("medicamento") and atual.get("apresentacao") and atual.get("local_bruto"))


def _parece_novo(cols: dict) -> bool:
    """Nome desalinhado acima do nº (tem dose/local; não é continuação curta)."""
    med = cols["medicamento"]
    apres = cols["apresentacao"]
    if not med or len(med) < 5 or not med[0].isalpha():
        return False
    if not cols["local"] or not apres:
        return False
    # Continuação curta de nome ("Sódica", "estolato"...).
    if len(med.split()) == 1 and len(med) <= 12:
        return False
    # Precisa de dose numérica na apresentação (evita "(gotas/frasco)").
    return bool(re.search(r"\d", apres) and _RE_DOSE.search(apres))


def _enriquecer(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza textos e expande locais de acesso."""
    df = df.copy()
    df["categoria"] = df["categoria"].fillna("").map(_limpar)
    for col in ("medicamento", "apresentacao", "local_bruto"):
        df[col] = df[col].fillna("").map(_limpar_campo)
    df["medicamento"] = df["medicamento"].str.replace(r"\s*\*+\s*$", "", regex=True)
    df["medicamento"] = df["medicamento"].map(_consertar_nome)
    df["nome_busca"] = df["medicamento"].map(_nome_busca)
    df["tem_ubs"] = df["local_bruto"].str.contains(r"\bUBS\b", case=False, na=False)
    df["tem_farmacia"] = df["local_bruto"].str.contains(
        r"Farm[aá]cia\s+Bom\s+Pastor", case=False, na=False
    )
    df.loc[~df["tem_ubs"] & ~df["tem_farmacia"], "tem_farmacia"] = True
    df["locais"] = df.apply(_expandir_locais, axis=1)
    df["qtd_locais"] = df["locais"].map(lambda xs: len(xs.split(" | ")) if xs else 0)
    df["observacao"] = df["local_bruto"].map(_obs_portaria)
    # Item 59 duplicado no PDF (Prednisona); mantém ordem de leitura.
    df.insert(0, "id", range(1, len(df) + 1))
    return df[
        [
            "id",
            "item",
            "categoria",
            "medicamento",
            "nome_busca",
            "apresentacao",
            "local_bruto",
            "locais",
            "qtd_locais",
            "tem_farmacia",
            "tem_ubs",
            "observacao",
        ]
    ]


def _consertar_nome(nome: str) -> str:
    """Junta sílabas quebradas comuns do PDF."""
    n = nome
    trocas = (
        (r"Benzilpenicilin\s+a\b", "Benzilpenicilina"),
        (r"Nitrofurantoín\s+a\b", "Nitrofurantoína"),
        (r"Sulfametoxaz\s+ol\b", "Sulfametoxazol"),
        (r"Dexclorfenira\s+mi\s+na\b", "Dexclorfeniramina"),
        (r"\(Benzoil\)Metro\s+ni\s+dazol", "(Benzoil)Metronidazol"),
        (r"Timolol,Maleat\s+o\b", "Timolol, Maleato"),
        (r"Metocloprami\s+da\b", "Metoclopramida"),
        (r"Ondansentron\s+a\b", "Ondansetrona"),
        (r"Carbamazepin\s+a\b", "Carbamazepina"),
        (r"Clorpromazin\s+a\b", "Clorpromazina"),
        (r"Levonorgestre\s+l\b", "Levonorgestrel"),
        (r"Medroxiproge\s+st\s+erona", "Medroxiprogesterona"),
        (r"Noretistero\s+na\b", "Noretisterona"),
        (r"hidrocortitison\s+a\b", "hidrocortisona"),
        (r"Beclometason\s+a\b", "Beclometasona"),
        (r"\+Clavulanato", "+ Clavulanato"),
        (r"\s+\+\s*", " + "),
    )
    for pad, rep in trocas:
        n = re.sub(pad, rep, n, flags=re.I)
    return _limpar(n)


def _expandir_locais(row: pd.Series) -> str:
    """Farmácia Bom Pastor e/ou lista de UBS do município."""
    locais: list[str] = []
    if row["tem_farmacia"]:
        locais.append(FARMACIA_REF)
    if row["tem_ubs"]:
        locais.extend(f"UBS {b}" for b in UBS_BAIRROS)
    return " | ".join(locais)


def _obs_portaria(texto: str) -> str:
    if not texto:
        return ""
    m = re.search(r"\(Port[^)]*\)", texto, flags=re.I)
    return _limpar(m.group(0)) if m else ""


def _nome_busca(nome: str) -> str:
    """Nome principal para o combobox."""
    base = re.split(r"[,–]", nome, maxsplit=1)[0]
    base = re.sub(r"\s*\([^)]*\)\s*", " ", base)
    base = _limpar(base).title()
    # Evita sobras de sal/radical sozinhas no combobox.
    if len(base) <= 4:
        return _limpar(nome).title()
    return base


def _limpar_campo(texto: str) -> str:
    """Remove restos de cabeçalho colados no campo."""
    if not texto:
        return ""
    partes = []
    for tok in texto.split():
        if _norm(tok) in _LIXO:
            continue
        partes.append(tok)
    return _limpar(" ".join(partes))


def _limpar(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "").replace("\n", " ")).strip()


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().lower()


def main() -> None:
    """CLI: PDF → CSV processado."""
    raiz = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Processa REMUME.pdf")
    parser.add_argument("--input", type=Path, default=raiz / "data" / "bruto" / "REMUME.pdf")
    parser.add_argument(
        "--output", type=Path, default=raiz / "data" / "processed" / "remume.csv"
    )
    args = parser.parse_args()
    df = processar(args.input, args.output)
    print(f"Itens: {len(df)} → {args.output}")
    print(df.categoria.value_counts().to_string())
    print(df[["item", "categoria", "medicamento", "tem_ubs"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
