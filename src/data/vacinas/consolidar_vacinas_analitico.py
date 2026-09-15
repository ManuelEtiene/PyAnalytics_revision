from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "vacinas"
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "bruto" / "vacinas"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "vacinas_analitico.csv"

RAW_REPROCESS_FILENAMES = {
    "arapongas.csv": ("Arapongas", "Arapongas"),
    "divineia.csv": ("Divineia", "Divineia"),
    "hercilio_luz.csv": ("Hercilio Luz", "Hercilio Luz"),
    "jardim_das_avenidas.csv": ("Jardim das Avenidas", "Jardim das Avenidas"),
}

OUTPUT_COLUMNS = [
    "nome_do_bairro",
    "nome_da_vacina",
    "codigo_da_vacina",
    "estrategia",
    "codigo_da_estrategia",
    "dose",
    "codigo_da_dose",
    "vacina_estrategia_e_dose",
    "lote",
    "validade_do_lote",
    "data_da_aplicacao",
    "origem",
]

BAIRRO_BY_RAW_DIR = {
    "Arapongas": "Arapongas",
    "Bom Pastor": "Bom Pastor",
    "Cidade Alta": "Cidade Alta",
    "Coloninha": "Coloninha",
    "Divineia": "Divineia",
    "Hercilio Luz": "Hercilio Luz",
    "Jardim Cibele": "Jardim Cibele",
    "Jardim das Avenidas": "Jardim das Avenidas",
    "Mato Alto Lagoao": "Mato Alto Lagoao",
    "Morro dos Conventos": "Morro dos Conventos",
    "Policia Rodoviaria": "Policia Rodoviaria",
    "Sanga da Areia": "Sanga da Areia",
    "Sanga da Toca": "Sanga da Toca",
    "Urussanguinha": "Urussanguinha",
    "Vila Sao Jose": "Vila Sao Jose",
}

BAIRRO_NAME_FIXES = {
    "Hercilio Luz": "Hercilio Luz",
    "Mato Alto Lagoao": "Mato Alto Lagoao",
    "Policia Rodoviaria": "Policia Rodoviaria",
    "Vila Sao Jose": "Vila Sao Jose",
}


def compact_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\ufeff", "").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalize_key(value: str) -> str:
    value = compact_text(value).lower()
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value


def is_application_date(value: str) -> bool:
    value = compact_text(value)
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
        day, month, _ = [int(part) for part in value.split("/")]
        return 1 <= day <= 31 and 1 <= month <= 12
    if re.fullmatch(r"\d{2}/\d{4}", value):
        month = int(value.split("/")[0])
        return 1 <= month <= 12
    if value == "XX/XXXX":
        return True
    return False


def normalize_application_date(value: str) -> str:
    value = compact_text(value)
    if value == "XX/XXXX":
        return ""
    if re.fullmatch(r"\d{2}/\d{4}", value):
        return f"01/{value}"
    return value if is_application_date(value) else ""


def normalize_full_date(value: str) -> str:
    value = compact_text(value)
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
        return ""
    day, month, _ = [int(part) for part in value.split("/")]
    return value if 1 <= day <= 31 and 1 <= month <= 12 else ""


def label_and_code(value: str) -> tuple[str, str]:
    value = compact_text(value).rstrip("-").strip()
    match = re.fullmatch(r"(.+?)\s*\((\d+)\)", value)
    if not match:
        return value, ""
    return compact_text(match.group(1)), match.group(2)


def infer_dose_code(dose: str) -> str:
    normalized = unicodedata.normalize("NFKD", dose.upper())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    if "1" in normalized and "REFOR" not in normalized:
        return "1"
    if "2" in normalized and "REFOR" not in normalized:
        return "2"
    if "3" in normalized and "REFOR" not in normalized:
        return "3"
    if "4" in normalized and "REFOR" not in normalized:
        return "4"
    if "UNICA" in normalized:
        return "8"
    if "1" in normalized and "REFOR" in normalized:
        return "39"
    if "2" in normalized and "REFOR" in normalized:
        return "40"
    if "REFOR" in normalized:
        return "38"
    if normalized == "DOSE":
        return "9"
    return ""


def split_vaccine_strategy_dose(value: str) -> tuple[str, str, str, str, str, str]:
    value = compact_text(value)
    parts = [compact_text(part) for part in re.split(r"\s+-\s*", value)]
    vaccine, vaccine_code = label_and_code(parts[0] if len(parts) > 0 else "")
    strategy, strategy_code = label_and_code(parts[1] if len(parts) > 1 else "")
    dose, dose_code = label_and_code(parts[2] if len(parts) > 2 else "")
    if vaccine == "Vacina COVID-19-RNAm, Pfizer (Comirnaty) pediátrica menor de":
        vaccine = "Vacina COVID-19-RNAm, Pfizer (Comirnaty) pediátrica menor de 5 anos"
        vaccine_code = "102"
        strategy = strategy or "Rotina"
        strategy_code = strategy_code or "1"
    if dose and not dose_code:
        dose_code = infer_dose_code(dose)
    return vaccine, vaccine_code, strategy, strategy_code, dose, dose_code


def split_lote_validade(value: str) -> tuple[str, str]:
    value = compact_text(value)
    match = re.fullmatch(r"(.+?)\s+-\s+(\d{2}/\d{2}/\d{4})", value)
    if not match:
        return value, ""
    return compact_text(match.group(1)), normalize_full_date(match.group(2))


def normalize_origin(value: str) -> str:
    value = compact_text(value)
    if value == "Tela de":
        return "Tela de Aplicação"
    if value == "Origem":
        return ""
    return value


def read_csv_rows(path: Path) -> list[list[str]]:
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            with path.open("r", encoding=encoding, newline="") as file:
                return list(csv.reader(file))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"could not decode {path}")


def sniff_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def parse_raw_report(path: Path, bairro: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_row in read_csv_rows(path):
        row = [compact_text(value) for value in raw_row]
        if "XXX" not in row or len(row) < 8:
            continue

        vacina_estrategia_dose = row[4] if len(row) > 4 else ""
        if not vacina_estrategia_dose or vacina_estrategia_dose.startswith("Vacina,"):
            continue

        lote, validade = split_lote_validade(row[7] if len(row) > 7 else "")
        data_aplicacao, origem = "", ""

        for idx in range(8, min(len(row), 12)):
            value = row[idx]
            if not data_aplicacao and is_application_date(value):
                data_aplicacao = normalize_application_date(value)
                continue
            if value and value != "1" and not is_application_date(value):
                origem = value

        if not lote and not data_aplicacao and not origem:
            continue

        vacina, cod_vacina, estrategia, cod_estrategia, dose, cod_dose = (
            split_vaccine_strategy_dose(vacina_estrategia_dose)
        )
        rows.append(
            {
                "nome_do_bairro": BAIRRO_NAME_FIXES.get(bairro, bairro),
                "nome_da_vacina": vacina,
                "codigo_da_vacina": cod_vacina,
                "estrategia": estrategia,
                "codigo_da_estrategia": cod_estrategia,
                "dose": dose,
                "codigo_da_dose": cod_dose,
                "vacina_estrategia_e_dose": vacina_estrategia_dose,
                "lote": lote,
                "validade_do_lote": validade,
                "data_da_aplicacao": data_aplicacao,
                "origem": normalize_origin(origem),
            }
        )
    return rows


def parse_processed_csv(path: Path) -> list[dict[str, str]]:
    delimiter = sniff_delimiter(path)
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        if not reader.fieldnames:
            return []

        field_by_key = {normalize_key(name): name for name in reader.fieldnames}
        rows: list[dict[str, str]] = []
        for raw in reader:
            normalized = {
                column: compact_text(raw.get(field_by_key.get(column, ""), ""))
                for column in OUTPUT_COLUMNS
            }

            if normalized["vacina_estrategia_e_dose"].startswith("Vacina,"):
                continue
            if normalized["data_da_aplicacao"] in {"Aplicado", "Qtde.", "1", "01/1"}:
                normalized["data_da_aplicacao"] = ""
            normalized["origem"] = normalize_origin(normalized["origem"])
            normalized["data_da_aplicacao"] = normalize_application_date(
                normalized["data_da_aplicacao"]
            )
            normalized["validade_do_lote"] = normalize_full_date(
                normalized["validade_do_lote"]
            )

            if normalized["vacina_estrategia_e_dose"]:
                parsed = split_vaccine_strategy_dose(normalized["vacina_estrategia_e_dose"])
                for column, value in zip(OUTPUT_COLUMNS[1:7], parsed):
                    if value and not normalized[column]:
                        normalized[column] = value

            if normalized["nome_da_vacina"]:
                rows.append(normalized)
        return rows


def find_raw_files(raw_dir: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for dirname, bairro in BAIRRO_BY_RAW_DIR.items():
        folder = raw_dir / dirname
        matches = sorted(folder.glob("*.csv"))
        if matches:
            files[bairro] = matches[0]
    return files


def find_single_raw_csv(raw_dir: Path, raw_subdir: str) -> Path:
    matches = sorted((raw_dir / raw_subdir).glob("*.csv"))
    if not matches:
        raise FileNotFoundError(f"Nenhum CSV bruto encontrado em {raw_dir / raw_subdir}")
    return matches[0]


def consolidate(processed_dir: Path, raw_dir: Path) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    notes: list[str] = []

    for path in sorted(processed_dir.glob("*.csv")):
        if path.name == "vacinas_analitico.csv":
            continue

        if path.name in RAW_REPROCESS_FILENAMES:
            raw_subdir, bairro = RAW_REPROCESS_FILENAMES[path.name]
            raw_path = find_single_raw_csv(raw_dir, raw_subdir)
            parsed = parse_raw_report(raw_path, bairro)
            rows.extend(parsed)
            notes.append(
                f"{path.name}: {len(parsed)} linhas refeitas a partir do bruto {raw_path.name}"
            )
            continue

        parsed = parse_processed_csv(path)
        rows.extend(parsed)
        notes.append(f"{path.name}: {len(parsed)} linhas a partir do processado")
    return rows, notes


def write_output(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consolida as bases de vacinas por bairro em uma base analitica padronizada."
    )
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows, notes = consolidate(args.processed_dir, args.raw_dir)
    rows.sort(
        key=lambda row: (
            row["nome_do_bairro"],
            row["nome_da_vacina"],
            row["data_da_aplicacao"],
            row["lote"],
        )
    )
    write_output(rows, args.output)

    print(f"Arquivo gerado: {args.output}")
    print(f"Total de linhas: {len(rows)}")
    for note in notes:
        print(f"- {note}")


if __name__ == "__main__":
    main()
