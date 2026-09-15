from __future__ import annotations

import argparse
from pathlib import Path

from consolidar_vacinas_analitico import (
    DEFAULT_PROCESSED_DIR,
    DEFAULT_RAW_DIR,
    parse_processed_csv,
    parse_raw_report,
    write_output,
)


RAW_REPROCESS_TARGETS = {
    "arapongas.csv": ("Arapongas", "Arapongas"),
    "divineia.csv": ("Divineia", "Divineia"),
    "hercilio_luz.csv": ("Hercilio Luz", "Hercilio Luz"),
    "jardim_das_avenidas.csv": ("Jardim das Avenidas", "Jardim das Avenidas"),
}


def find_single_raw_csv(raw_dir: Path, raw_subdir: str) -> Path:
    matches = sorted((raw_dir / raw_subdir).glob("*.csv"))
    if not matches:
        raise FileNotFoundError(f"Nenhum CSV bruto encontrado em {raw_dir / raw_subdir}")
    return matches[0]


def reprocess_from_raw(raw_dir: Path, processed_dir: Path, filename: str) -> int:
    raw_subdir, bairro = RAW_REPROCESS_TARGETS[filename]
    raw_path = find_single_raw_csv(raw_dir, raw_subdir)
    rows = parse_raw_report(raw_path, bairro)
    write_output(rows, processed_dir / filename)
    return len(rows)


def normalize_processed_csv_dates(path: Path) -> int:
    rows = parse_processed_csv(path)
    write_output(rows, path)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Padroniza processados de vacinas: refaz os arquivos com colunas "
            "deslocadas a partir dos brutos e salva todos com delimitador ','."
        )
    )
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    args = parser.parse_args()

    for filename in RAW_REPROCESS_TARGETS:
        rows = reprocess_from_raw(args.raw_dir, args.processed_dir, filename)
        print(f"{filename}: {rows} linhas regeneradas a partir do bruto")

    for path in sorted(args.processed_dir.glob("*.csv")):
        if path.name in RAW_REPROCESS_TARGETS:
            continue
        rows = normalize_processed_csv_dates(path)
        print(f"{path.name}: {rows} linhas normalizadas")


if __name__ == "__main__":
    main()
