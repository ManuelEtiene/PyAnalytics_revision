#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
PAREN_SUFFIX_RE = re.compile(r"^(?P<nome>.*?)(?:\s*\((?P<codigo>[^()]*)\))?$")
COMPETENCIA_RE = re.compile(r"Compet[êe]ncia Inicial:\s*(\d+)")
COMPETENCIA_FINAL_RE = re.compile(r"Compet[êe]ncia Final:\s*(\d+)")
UPS_FILTRO_RE = re.compile(r"UPS:\s*(.*?)\s+Ordena")


OUTPUT_FIELDS = [
    "competencia_inicial",
    "competencia_final",
    "ups_nome",
    "ups_codigo",
    "bairro_nome",
    "bairro_codigo",
    "centro_custo_nome",
    "centro_custo_codigo",
    "material_nome",
    "material_codigo",
    "data",
    "saida",
    "usuario",
    "fabricante",
    "lote",
    "numero_receita",
    "validade",
    "quantidade",
    "custo_medio",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transforma relatórios CSV paginados de saída de materiais em tabela plana."
    )
    parser.add_argument(
        "entradas",
        nargs="+",
        help="Arquivos CSV e/ou diretórios contendo os relatórios.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="materiais_normalizados.csv",
        help="Arquivo CSV de saída.",
    )
    return parser.parse_args()


def split_name_code(text: str) -> tuple[str, str]:
    value = text.strip().rstrip(",")
    match = PAREN_SUFFIX_RE.match(value)
    if not match:
        return value, ""
    nome = (match.group("nome") or "").strip()
    codigo = (match.group("codigo") or "").strip()
    return nome, codigo


def normalize_context_value(raw_value: str, prefix: str) -> tuple[str, str]:
    value = raw_value.strip()
    if value.startswith(prefix):
        value = value[len(prefix) :].strip()
    return split_name_code(value)


def iter_input_files(entries: list[str]) -> list[Path]:
    files: list[Path] = []
    for entry in entries:
        path = Path(entry)
        if path.is_dir():
            files.extend(sorted(path.glob("*.csv")))
        elif path.suffix.lower() == ".csv":
            files.append(path)
    unique_files = []
    seen = set()
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            unique_files.append(path)
            seen.add(resolved)
    return unique_files


def first_non_empty_cell(row: list[str]) -> str:
    for cell in row:
        if cell.strip():
            return cell.strip()
    return ""


def parse_filter_line(text: str, context: dict[str, str]) -> None:
    compact = " ".join(text.replace("\xa0", " ").split())
    match = COMPETENCIA_RE.search(compact)
    if match:
        context["competencia_inicial"] = match.group(1)
    match = COMPETENCIA_FINAL_RE.search(compact)
    if match:
        context["competencia_final"] = match.group(1)
    match = UPS_FILTRO_RE.search(compact)
    if match and not context["ups_nome"]:
        ups_nome, ups_codigo = split_name_code(match.group(1))
        context["ups_nome"] = ups_nome
        context["ups_codigo"] = ups_codigo


def is_data_row(row: list[str]) -> bool:
    return len(row) > 17 and DATE_RE.match(row[3].strip() or "") is not None


def parse_data_fields(row: list[str]) -> dict[str, str]:
    tail = [(index, value.strip()) for index, value in enumerate(row[12:], start=12) if value.strip()]

    numero_receita = ""
    validade = ""
    quantidade = ""
    custo_medio = ""

    if tail and tail[-1][1].startswith("R$"):
        _, custo_medio = tail.pop()
    if tail:
        _, quantidade = tail.pop()
    if tail and DATE_RE.match(tail[-1][1]):
        _, validade = tail.pop()
    if tail:
        _, numero_receita = tail.pop(0)

    return {
        "data": row[3].strip(),
        "saida": row[6].strip() if len(row) > 6 else "",
        "usuario": row[7].strip() if len(row) > 7 else "",
        "fabricante": row[10].strip() if len(row) > 10 else "",
        "lote": row[11].strip() if len(row) > 11 else "",
        "numero_receita": numero_receita,
        "validade": validade,
        "quantidade": quantidade,
        "custo_medio": custo_medio,
    }


def parse_csv(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    context = {field: "" for field in OUTPUT_FIELDS}

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue

            text = first_non_empty_cell(row)
            if not text:
                continue

            if text.startswith("Filtros:"):
                parse_filter_line(text, context)
                continue
            if text.startswith("UPS:"):
                context["ups_nome"], context["ups_codigo"] = normalize_context_value(text, "UPS:")
                continue
            if text.startswith("Bairro:"):
                context["bairro_nome"], context["bairro_codigo"] = normalize_context_value(text, "Bairro:")
                continue
            if text.startswith("Centro de Custo:"):
                context["centro_custo_nome"], context["centro_custo_codigo"] = normalize_context_value(
                    text, "Centro de Custo:"
                )
                continue
            if text.startswith("Material:"):
                context["material_nome"], context["material_codigo"] = normalize_context_value(text, "Material:")
                continue

            if is_data_row(row):
                data_fields = parse_data_fields(row)
                rows.append(
                    {
                        "competencia_inicial": context["competencia_inicial"],
                        "competencia_final": context["competencia_final"],
                        "ups_nome": context["ups_nome"],
                        "ups_codigo": context["ups_codigo"],
                        "bairro_nome": context["bairro_nome"],
                        "bairro_codigo": context["bairro_codigo"],
                        "centro_custo_nome": context["centro_custo_nome"],
                        "centro_custo_codigo": context["centro_custo_codigo"],
                        "material_nome": context["material_nome"],
                        "material_codigo": context["material_codigo"],
                        **data_fields,
                    }
                )

    return rows


def write_output(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    input_files = iter_input_files(args.entradas)
    if not input_files:
        raise SystemExit("Nenhum arquivo CSV encontrado nas entradas informadas.")

    all_rows: list[dict[str, str]] = []
    for csv_path in input_files:
        all_rows.extend(parse_csv(csv_path))

    write_output(Path(args.output), all_rows)
    print(f"{len(all_rows)} linhas gravadas em {args.output}")


if __name__ == "__main__":
    main()
