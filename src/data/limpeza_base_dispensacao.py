#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATE_FIELDS = {"data", "validade"}
INTEGER_FIELDS = {"quantidade"}
CURRENCY_FIELDS = {"custo_medio"}
DEFAULT_REFERENCIA_PATH = Path("./Complementar/DADOS_ABERTOS_MEDICAMENTOS.csv")
TEXT_REPLACEMENTS = {
    "centro_custo_nome": {
        "Sem Centro de Custro": "Sem Centro de Custo",
    }
}
TEXT_FIELDS = {"ups_nome", "bairro_nome", "centro_custo_nome", "material_nome", "fabricante_nome"}
FABRICANTE_RE = re.compile(r"^\s*(\d+)\s*-\s*(.+?)\s*$")
MATCH_STOPWORDS = {
    "DE",
    "DA",
    "DO",
    "DAS",
    "DOS",
    "E",
    "EM",
    "COM",
    "PARA",
    "SEM",
    "MG",
    "ML",
    "MCG",
    "G",
    "UI",
    "UNIDADE",
    "UNIDADES",
    "COMPRIMIDO",
    "COMPRIMIDOS",
    "CAPSULA",
    "CAPSULAS",
    "FRASCO",
    "FRASCOS",
    "AMPOLA",
    "AMPOLAS",
    "CANETA",
    "CANETAS",
    "CARPULE",
    "TUBETE",
}
TIPO_TRATAMENTO_RULES = [
    (("ANTICONVULS", "ANSIOLIT", "ANTIDEPRESS", "ANTIPSIC", "ANTIPARKINSON", "HIPNOT", "SEDAT", "NEURO"), "Saude mental e neurologia"),
    (("ANTIULCER", "ANTIACID", "DIGEST", "INIBIDORES DA BOMBA DE PROTONS"), "Sistema digestivo"),
    (("ANTIDIABET", "INSULIN"), "Diabetes e endocrinologia"),
    (("ANTIBIOT", "ANTIMICROBI", "ANTIVIRO", "ANTIMICOT", "ANTIPARASIT"), "Infeccoes"),
    (("ANALGES", "ANTIINFLAM", "ANTIREUM", "RELAXANTES MUSCULARES", "ANTIESPASMOD"), "Dor e inflamacao"),
    (("ANTIHIPERTEN", "ANTIANGIN", "ANTICOAGUL", "ANTIAGREGANTE", "CARDIOVASC", "DIURET"), "Cardiovascular"),
    (("BRONCODILAT", "ANTIASMAT", "RESPIRAT"), "Respiratorio"),
    (("VITAMIN", "SUPLEMENT", "MINERAL"), "Vitaminas e suplementacao"),
    (("HORMON", "TIREOID", "CONTRACEPT"), "Hormonal e saude reprodutiva"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aplica limpeza de tipos e moeda em um CSV normalizado de materiais."
    )
    parser.add_argument("input_csv", help="CSV de entrada já normalizado.")
    parser.add_argument(
        "-o",
        "--output",
        default="materiais_limpos.csv",
        help="Arquivo CSV de saída.",
    )
    parser.add_argument(
        "--referencia-medicamentos",
        default=str(DEFAULT_REFERENCIA_PATH),
        help="CSV complementar com NOME_PRODUTO, PRINCIPIO_ATIVO e CLASSE_TERAPEUTICA.",
    )
    return parser.parse_args()


def normalize_date(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    return datetime.strptime(text, "%d/%m/%Y").date().isoformat()


def normalize_integer(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    return str(int(text))


def normalize_currency(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    cleaned = text.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return format(Decimal(cleaned), "f")
    except InvalidOperation as exc:
        raise ValueError(f"Valor monetário inválido: {value!r}") from exc


def normalize_text_fields(row: dict[str, str]) -> None:
    for field, replacements in TEXT_REPLACEMENTS.items():
        if field in row:
            row[field] = replacements.get(row[field], row[field]).strip()
    for field in TEXT_FIELDS:
        if field in row:
            row[field] = normalize_text(row[field])


def normalize_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" - - ", " - ")
    text = text.replace(" / ", "/")
    return text.strip()


def normalize_match_text(value: str) -> str:
    text = normalize_text(value).upper()
    text = "".join(char for char in unicodedata.normalize("NFKD", text) if not unicodedata.combining(char))
    text = text.replace("+", " ")
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize_match_text(value: str) -> set[str]:
    tokens = set()
    for token in normalize_match_text(value).split():
        if token not in MATCH_STOPWORDS and not token.isdigit():
            tokens.add(token)
    return tokens


def split_fabricante(value: str) -> tuple[str, str]:
    text = normalize_text(value)
    if not text:
        return "", ""
    match = FABRICANTE_RE.match(text)
    if not match:
        return "", text
    return match.group(1), match.group(2).strip()


def split_material(value: str) -> tuple[str, str, str]:
    text = normalize_text(value)
    if not text:
        return "", "", ""

    parts = [part.strip() for part in text.split(" - ") if part.strip()]
    if len(parts) >= 3:
        return parts[0], " - ".join(parts[1:-1]), parts[-1]
    if len(parts) == 2:
        return parts[0], "", parts[1]
    return text, "", ""


def infer_tipo_tratamento(classe_terapeutica: str) -> str:
    normalized = normalize_match_text(classe_terapeutica)
    if not normalized:
        return ""
    for keywords, tipo in TIPO_TRATAMENTO_RULES:
        if any(keyword in normalized for keyword in keywords):
            return tipo
    return "Outros"


def load_referencia_medicamentos(path: Path) -> tuple[dict[str, str], list[tuple[set[str], str]]]:
    exact_lookup: dict[str, Counter[str]] = {}
    fuzzy_entries: list[tuple[set[str], str]] = []

    with path.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            classe = normalize_text(row.get("CLASSE_TERAPEUTICA", ""))
            if not classe:
                continue

            texts = [row.get("NOME_PRODUTO", ""), row.get("PRINCIPIO_ATIVO", "")]
            texts.extend(part.strip() for part in (row.get("PRINCIPIO_ATIVO", "") or "").split(","))

            for text in texts:
                normalized = normalize_match_text(text)
                if not normalized:
                    continue
                exact_lookup.setdefault(normalized, Counter())[classe] += 1

                tokens = tokenize_match_text(text)
                if tokens:
                    fuzzy_entries.append((tokens, classe))

    collapsed_lookup = {key: counter.most_common(1)[0][0] for key, counter in exact_lookup.items()}
    return collapsed_lookup, fuzzy_entries


def match_classe_terapeutica(material_nome_base: str, exact_lookup: dict[str, str], fuzzy_entries: list[tuple[set[str], str]]) -> str:
    normalized = normalize_match_text(material_nome_base)
    if not normalized:
        return ""
    if normalized in exact_lookup:
        return exact_lookup[normalized]

    material_tokens = tokenize_match_text(material_nome_base)
    if not material_tokens:
        return ""

    best_score = 0.0
    class_scores: Counter[str] = Counter()
    for reference_tokens, classe in fuzzy_entries:
        intersection = material_tokens & reference_tokens
        if not intersection:
            continue
        score = len(intersection) / len(material_tokens)
        if score < 0.6:
            continue
        if score > best_score:
            best_score = score
            class_scores = Counter({classe: 1})
        elif score == best_score:
            class_scores[classe] += 1

    if not class_scores:
        return ""
    return class_scores.most_common(1)[0][0]


def clean_row(
    row: dict[str, str],
    exact_lookup: dict[str, str],
    fuzzy_entries: list[tuple[set[str], str]],
) -> dict[str, str]:
    cleaned = dict(row)
    normalize_text_fields(cleaned)
    for field in DATE_FIELDS:
        if field in cleaned:
            cleaned[field] = normalize_date(cleaned[field])
    for field in INTEGER_FIELDS:
        if field in cleaned:
            cleaned[field] = normalize_integer(cleaned[field])
    for field in CURRENCY_FIELDS:
        if field in cleaned:
            cleaned[field] = normalize_currency(cleaned[field])
    fabricante_codigo, fabricante_nome = split_fabricante(cleaned.get("fabricante", ""))
    cleaned.pop("fabricante", None)
    cleaned["fabricante_codigo"] = fabricante_codigo
    cleaned["fabricante_nome"] = fabricante_nome
    material_nome_base, material_descricao_complementar, material_tipo = split_material(
        cleaned.get("material_nome", "")
    )
    cleaned["material_nome_base"] = material_nome_base
    cleaned["material_descricao_complementar"] = material_descricao_complementar
    cleaned["material_tipo"] = material_tipo
    cleaned["classe_terapeutica"] = match_classe_terapeutica(material_nome_base, exact_lookup, fuzzy_entries)
    cleaned["tipo_tratamento"] = infer_tipo_tratamento(cleaned["classe_terapeutica"])
    return cleaned


def build_output_fieldnames(input_fieldnames: list[str]) -> list[str]:
    output = []
    for field in input_fieldnames:
        if field == "fabricante":
            output.extend(["fabricante_codigo", "fabricante_nome"])
            continue
        if field == "material_nome":
            output.extend(
                [
                    "material_nome",
                    "material_nome_base",
                    "material_descricao_complementar",
                    "material_tipo",
                    "classe_terapeutica",
                    "tipo_tratamento",
                ]
            )
            continue
        output.append(field)
    return output


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_csv)
    output_path = Path(args.output)
    referencia_path = Path(args.referencia_medicamentos)
    exact_lookup, fuzzy_entries = load_referencia_medicamentos(referencia_path)

    with input_path.open("r", encoding="utf-8", newline="") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise SystemExit("CSV de entrada sem cabeçalho.")
        output_fieldnames = build_output_fieldnames(reader.fieldnames)

        with output_path.open("w", encoding="utf-8", newline="") as dst:
            writer = csv.DictWriter(dst, fieldnames=output_fieldnames)
            writer.writeheader()

            total = 0
            for row in reader:
                writer.writerow(clean_row(row, exact_lookup, fuzzy_entries))
                total += 1

    print(f"{total} linhas gravadas em {output_path}")


if __name__ == "__main__":
    main()
