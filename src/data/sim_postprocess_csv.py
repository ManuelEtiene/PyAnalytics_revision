"""Pos-processa CSVs do SIM ja gerados pelo pipeline.

Normaliza campos canonicos, adiciona colunas auxiliares e pode gerar uma
versao analitica mais enxuta sem exigir reprocessamento dos dados brutos.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.sim_pipeline import is_sc_municipality_code, normalize_null, parse_sim_date

LEGACY_COLUMNS = ["MUNIRES", "MUNIOCOR", "DATAOBITO", "DATANASC"]
ADDITIONAL_COLUMNS = [
    "CODMUNRES",
    "CODMUNOCOR",
    "DTOBITO_BRUTO",
    "DTNASC_BRUTO",
    "DTOBITO",
    "DTNASC",
    "ANO_OBITO",
    "ANO_NASC",
    "DATA_OBITO_VALIDA",
    "DATA_NASC_VALIDA",
    "SC_RESIDENCIA",
    "SC_OCORRENCIA",
]

# Alguns layouts historicos do SIM usam estes nomes. Os campos canonicos sao
# preenchidos sem apagar os campos de origem, o que mantem o arquivo completo
# auditavel e da ao modo ``analytic`` um esquema consistente entre os anos.
CANONICAL_ALIASES = {
    "ESTCIV": ("ESTCIVIL",),
    "OCUP": ("OCUPACAO",),
    "QTDFILVIVO": ("FILHVIVOS",),
    "QTDFILMORT": ("FILHMORT",),
    "GRAVIDEZ": ("TIPOGRAV",),
    "PARTO": ("TIPOPARTO",),
    "PESO": ("PESONASC",),
    "SEMAGESTAC": ("SEMANGEST",),
}

# O modo analytic e deliberadamente mais amplo que uma analise especifica.
# Ele retem dimensoes demograficas, temporais, territoriais, assistenciais e
# de causa/circunstancia que sao recorrentes em estudos epidemiologicos.
ANALYTIC_COLUMNS = [
    "CONTADOR",
    "TIPOBITO",
    "DTOBITO",
    "HORAOBITO",
    "NATURAL",
    "CODMUNNATU",
    "DTNASC",
    "IDADE",
    "SEXO",
    "RACACOR",
    "ESTCIV",
    "ESC",
    "ESC2010",
    "SERIESCFAL",
    "OCUP",
    "CODMUNRES",
    "LOCOCOR",
    "CODMUNOCOR",
    "CODESTAB",
    "ESTABDESCR",
    "IDADEMAE",
    "ESCMAE",
    "ESCMAE2010",
    "SERIESCMAE",
    "OCUPMAE",
    "QTDFILVIVO",
    "QTDFILMORT",
    "GRAVIDEZ",
    "GESTACAO",
    "SEMAGESTAC",
    "PARTO",
    "OBITOPARTO",
    "PESO",
    "OBITOGRAV",
    "OBITOPUERP",
    "ASSISTMED",
    "EXAME",
    "CIRURGIA",
    "NECROPSIA",
    "CAUSABAS",
    "CAUSAMAT",
    "LINHAA",
    "LINHAB",
    "LINHAC",
    "LINHAD",
    "LINHAII",
    "CIRCOBITO",
    "ACIDTRAB",
    "FONTE",
    "TPMORTEOCO",
    "MORTEPARTO",
    "TPOBITOCOR",
    "NUDIASOBIN",
    "NUDIASOBCO",
    "MAT_CLAS",
    "ETNIA",
    "AREARES",
    "CRSRES",
    "CRSOCOR",
    "DTOBITO_BRUTO",
    "DTNASC_BRUTO",
    "SEXO_COD",
    "RACACOR_COD",
    "LOCOCOR_COD",
    "IDADE_COD",
    "IDADE_ANOS",
    "ANO_OBITO",
    "ANO_NASC",
    "DATA_OBITO_VALIDA",
    "DATA_NASC_VALIDA",
    "SC_RESIDENCIA",
    "SC_OCORRENCIA",
]

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Pos-processa um CSV do SIM ja gerado, adicionando colunas auxiliares "
            "e organizando campos canonicos sem reler os arquivos brutos."
        )
    )
    parser.add_argument("--input", type=Path, help="CSV de entrada.")
    parser.add_argument(
        "--output",
        type=Path,
        help="CSV de saida. Pode ser o mesmo caminho da entrada.",
    )
    parser.add_argument(
        "--mode",
        choices=["complete", "analytic"],
        default="complete",
        help=(
            "Modo complete preserva o dataset amplo ja normalizado. Modo analytic gera "
            "uma versao enxuta apenas com colunas confiaveis para analise."
        ),
    )
    parser.add_argument(
        "--keep-legacy-columns",
        action="store_true",
        help="Mantem MUNIRES/MUNIOCOR/DATAOBITO/DATANASC no CSV final.",
    )
    parser.add_argument(
        "--list-analytic-columns",
        action="store_true",
        help="Lista as colunas da versao analitica e encerra.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.list_analytic_columns:
        return
    if args.input is None or args.output is None:
        raise ValueError("Informe --input e --output, exceto ao usar --list-analytic-columns")
    if not args.input.exists():
        raise ValueError(f"Arquivo de entrada nao encontrado: {args.input}")
    if args.input.suffix.lower() != ".csv" or args.output.suffix.lower() != ".csv":
        raise ValueError("Entrada e saida devem ser arquivos .csv")


def parse_existing_or_raw_date(value: Any) -> str | None:
    value = normalize_null(value)
    if value is None:
        return None

    text = str(value).strip()
    if ISO_DATE_RE.fullmatch(text):
        return text
    return parse_sim_date(text)


def extract_year_from_iso_date(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value[:4])
    except (TypeError, ValueError):
        return None


def resolve_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = normalize_null(row.get(key))
        if value is not None:
            return value
    return None


def build_output_fieldnames(input_fieldnames: list[str], *, keep_legacy_columns: bool, mode: str) -> list[str]:
    fieldnames: list[str] = []
    seen: set[str] = set()
    legacy_to_drop = set() if keep_legacy_columns else set(LEGACY_COLUMNS)

    for field in input_fieldnames:
        if field in legacy_to_drop:
            continue
        if field not in seen:
            fieldnames.append(field)
            seen.add(field)

    for field in (*ADDITIONAL_COLUMNS, *CANONICAL_ALIASES):
        if field not in seen:
            fieldnames.append(field)
            seen.add(field)

    if mode == "analytic":
        # O schema analitico deve ser estavel mesmo se um campo nao existir em
        # determinado ano/layout. Nesse caso a coluna e mantida vazia, em vez
        # de desaparecer e quebrar consultas que combinam varios anos.
        return list(ANALYTIC_COLUMNS)

    return fieldnames


def postprocess_row(row: dict[str, Any], *, keep_legacy_columns: bool) -> dict[str, Any]:
    processed = dict(row)

    for canonical_name, aliases in CANONICAL_ALIASES.items():
        processed[canonical_name] = resolve_value(
            processed, canonical_name, *aliases
        )

    municipality_residence = resolve_value(processed, "CODMUNRES", "MUNIRES")
    municipality_occurrence = resolve_value(processed, "CODMUNOCOR", "MUNIOCOR")
    date_of_death_raw = resolve_value(processed, "DTOBITO_BRUTO", "DTOBITO", "DATAOBITO")
    date_of_birth_raw = resolve_value(processed, "DTNASC_BRUTO", "DTNASC", "DATANASC")
    date_of_death = parse_existing_or_raw_date(resolve_value(processed, "DTOBITO", "DTOBITO_BRUTO", "DATAOBITO"))
    date_of_birth = parse_existing_or_raw_date(resolve_value(processed, "DTNASC", "DTNASC_BRUTO", "DATANASC"))

    if not keep_legacy_columns:
        for field in LEGACY_COLUMNS:
            processed.pop(field, None)

    processed["CODMUNRES"] = municipality_residence
    processed["CODMUNOCOR"] = municipality_occurrence
    processed["DTOBITO_BRUTO"] = date_of_death_raw
    processed["DTNASC_BRUTO"] = date_of_birth_raw
    processed["DTOBITO"] = date_of_death
    processed["DTNASC"] = date_of_birth
    processed["ANO_OBITO"] = extract_year_from_iso_date(date_of_death)
    processed["ANO_NASC"] = extract_year_from_iso_date(date_of_birth)
    processed["DATA_OBITO_VALIDA"] = date_of_death is not None
    processed["DATA_NASC_VALIDA"] = date_of_birth is not None
    processed["SC_RESIDENCIA"] = is_sc_municipality_code(municipality_residence)
    processed["SC_OCORRENCIA"] = is_sc_municipality_code(municipality_occurrence)
    return processed


def run_postprocess(input_path: Path, output_path: Path, *, keep_legacy_columns: bool, mode: str) -> int:
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV de entrada sem cabecalho")

        fieldnames = build_output_fieldnames(list(reader.fieldnames), keep_legacy_columns=keep_legacy_columns, mode=mode)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        same_file = input_path.resolve() == output_path.resolve()

        if same_file:
            with NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=output_path.parent, suffix=".csv") as tmp_handle:
                temp_path = Path(tmp_handle.name)
                writer = csv.DictWriter(tmp_handle, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                rows_written = 0
                for row in reader:
                    writer.writerow(postprocess_row(row, keep_legacy_columns=keep_legacy_columns))
                    rows_written += 1
            temp_path.replace(output_path)
            return rows_written

        with output_path.open("w", encoding="utf-8", newline="") as out_handle:
            writer = csv.DictWriter(out_handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            rows_written = 0
            for row in reader:
                writer.writerow(postprocess_row(row, keep_legacy_columns=keep_legacy_columns))
                rows_written += 1
        return rows_written


def main() -> int:
    try:
        args = parse_args()
        validate_args(args)
        if args.list_analytic_columns:
            print("\n".join(ANALYTIC_COLUMNS))
            return 0
        rows_written = run_postprocess(input_path=args.input, output_path=args.output, keep_legacy_columns=args.keep_legacy_columns, mode=args.mode)
    except Exception as exc:
        print(f"[erro] {exc}")
        return 1

    print(f"Pos-processamento concluido. modo={args.mode} linhas_escritas={rows_written} arquivo_saida={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
