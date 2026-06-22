"""Ingestao e transformacao basica dos dados do SIM via API.

O fluxo foi simplificado para o endpoint oficial do SIM:
- a API e paginada com `limit` e `offset`;
- cada lote e processado assim que chega;
- apenas registros de Santa Catarina sao mantidos no CSV final;
- o progresso e salvo em um arquivo de estado para permitir retomada.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from socket import timeout as SocketTimeout
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SIM_API_URL = (
    "https://apidadosabertos.saude.gov.br/"
    "vigilancia-e-meio-ambiente/sistema-de-informacao-sobre-mortalidade"
)

MAX_API_LIMIT = 1000

NULL_STRINGS = {
    "",
    " ",
    "NA",
    "N/A",
    "NAN",
    "NONE",
    "NULL",
    "NULO",
    "N/A.",
}

SEXO_MAP = {
    "1": "Masculino",
    "M": "Masculino",
    "2": "Feminino",
    "F": "Feminino",
    "0": "Ignorado",
    "9": "Ignorado",
    "I": "Ignorado",
}

RACACOR_MAP = {
    "1": "Branca",
    "2": "Preta",
    "3": "Amarela",
    "4": "Parda",
    "5": "Indigena",
    "9": "Ignorado",
}

LOCOCOR_MAP = {
    "1": "Hospital",
    "2": "Outro estabelecimento de saude",
    "3": "Domicilio",
    "4": "Via publica",
    "5": "Outros",
    "6": "Aldeia indigena",
    "9": "Ignorado",
}

DERIVED_COLUMNS = [
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


@dataclass
class BatchResult:
    rows_seen: int
    rows_kept: int
    rows_written: int
    next_offset: int


@dataclass
class LocalFileResult:
    source: Path
    output: Path | None
    rows_seen: int
    rows_kept: int
    rows_written: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recupera dados do SIM via API ou CSV local, filtra Santa Catarina "
            "durante a ingestao e grava saidas incrementais."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Arquivo CSV local do SIM para processamento offline.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Diretorio com arquivos CSV anuais do SIM para processamento em lote.",
    )
    parser.add_argument(
        "--api-url",
        default=SIM_API_URL,
        help=f"URL da API do SIM. Padrao: {SIM_API_URL}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/sim_sc_processado.csv"),
        help="CSV consolidado de saida.",
    )
    parser.add_argument(
        "--yearly-output-dir",
        type=Path,
        help=(
            "Diretorio para gravar uma saida por arquivo/ano ao processar CSVs "
            "locais."
        ),
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        help="Diretorio opcional para salvar cada resposta bruta da API em JSON.",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        help=(
            "Arquivo de estado para retomar o processamento. "
            "Padrao: mesmo nome do CSV com sufixo .state.json."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_API_LIMIT,
        help="Quantidade de itens por pagina. Deve ser <= 1000. Padrao: 1000.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help=(
            "Pagina inicial da API. O endpoint conta paginas a partir de 0. "
            "Padrao: 0."
        ),
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Numero maximo de paginas a processar nesta execucao.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help=(
            "Timeout por requisicao HTTP em segundos. Padrao: 1800 "
            "(30 minutos)."
        ),
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="Quantidade de novas tentativas apos falha transitoria. Padrao: 4.",
    )
    parser.add_argument(
        "--retry-wait",
        type=int,
        default=15,
        help="Segundos de espera entre tentativas. Padrao: 15.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Ignora qualquer estado salvo e recomeca do offset informado.",
    )
    parser.add_argument(
        "--sc-scope",
        choices=["residence", "occurrence", "residence_or_occurrence"],
        default="residence_or_occurrence",
        help=(
            "Regra para manter apenas registros de SC. "
            "Padrao: residence_or_occurrence."
        ),
    )

    args = parser.parse_args()
    validate_args(args)
    return args


def validate_args(args: argparse.Namespace) -> None:
    if args.input and args.input_dir:
        raise ValueError("Use apenas um entre --input e --input-dir.")
    if args.input_dir is not None and args.yearly_output_dir is None:
        raise ValueError(
            "Ao usar --input-dir, informe tambem --yearly-output-dir para gerar "
            "as saidas por ano antes da consolidacao."
        )
    if args.limit < 1 or args.limit > MAX_API_LIMIT:
        raise ValueError(
            f"O parametro --limit deve ficar entre 1 e {MAX_API_LIMIT}."
        )
    if args.offset < 0:
        raise ValueError("O parametro --offset nao pode ser negativo.")
    if args.max_pages is not None and args.max_pages < 1:
        raise ValueError("O parametro --max-pages deve ser maior que zero.")
    if args.timeout < 1:
        raise ValueError("O parametro --timeout deve ser maior que zero.")
    if args.retries < 0:
        raise ValueError("O parametro --retries nao pode ser negativo.")
    if args.retry_wait < 0:
        raise ValueError("O parametro --retry-wait nao pode ser negativo.")
    if args.input is not None and args.input.suffix.lower() != ".csv":
        raise ValueError("O modo local atualmente aceita apenas arquivos .csv.")
    if args.input_dir is not None and not args.input_dir.is_dir():
        raise ValueError("O caminho informado em --input-dir nao e um diretorio.")


def normalize_null(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        candidate = value.strip()
        if candidate.upper() in NULL_STRINGS:
            return None
        return candidate

    return value


def uppercase_keys(record: dict[str, Any]) -> dict[str, Any]:
    return {str(key).upper(): normalize_null(value) for key, value in record.items()}


def parse_sim_date(value: Any) -> str | None:
    value = normalize_null(value)
    if value is None:
        return None

    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return None

    try:
        if len(digits) == 8:
            return datetime.strptime(digits, "%d%m%Y").date().isoformat()
        if len(digits) == 6:
            return datetime.strptime(digits, "%y%m%d").date().isoformat()
    except ValueError:
        return None

    return None


def extract_year_from_iso_date(value: str | None) -> int | None:
    if not value:
        return None

    try:
        return int(value[:4])
    except (TypeError, ValueError):
        return None


def map_code(value: Any, mapping: dict[str, str]) -> str | None:
    value = normalize_null(value)
    if value is None:
        return None

    normalized = str(value).strip().upper()
    return mapping.get(normalized, "Ignorado")


def decode_sim_age_to_years(value: Any) -> float | None:
    """Decodifica a regra de idade do SIM em anos.

    Convencao utilizada no SIM:
    - 0xx: minutos
    - 1xx: horas
    - 2xx: dias
    - 3xx: meses
    - 4xx: anos
    - 5xx: 100 anos ou mais (100 + quantidade)
    - 9xx: ignorado
    """

    value = normalize_null(value)
    if value is None:
        return None

    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return None

    digits = digits.zfill(3)
    unit = digits[0]
    amount = int(digits[1:])

    if unit == "0":
        return round(amount / (60 * 24 * 365.25), 6)
    if unit == "1":
        return round(amount / (24 * 365.25), 6)
    if unit == "2":
        return round(amount / 365.25, 6)
    if unit == "3":
        return round(amount / 12, 6)
    if unit == "4":
        return float(amount)
    if unit == "5":
        return float(100 + amount)
    return None


def resolve_record_value(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = normalize_null(record.get(key))
        if value is not None:
            return value
    return None


def is_sc_municipality_code(value: Any) -> bool:
    value = normalize_null(value)
    if value is None:
        return False

    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits.startswith("42")


def keep_sc_record(record: dict[str, Any], scope: str) -> bool:
    by_residence = is_sc_municipality_code(
        resolve_record_value(record, "CODMUNRES", "MUNIRES")
    )
    by_occurrence = is_sc_municipality_code(
        resolve_record_value(record, "CODMUNOCOR", "MUNIOCOR")
    )

    if scope == "residence":
        return by_residence
    if scope == "occurrence":
        return by_occurrence
    return by_residence or by_occurrence


def transform_record(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    date_of_death = resolve_record_value(record, "DTOBITO", "DATAOBITO")
    date_of_birth = resolve_record_value(record, "DTNASC", "DATANASC")
    municipality_residence = resolve_record_value(record, "CODMUNRES", "MUNIRES")
    municipality_occurrence = resolve_record_value(record, "CODMUNOCOR", "MUNIOCOR")
    sexo_code = resolve_record_value(record, "SEXO")
    racacor_code = resolve_record_value(record, "RACACOR")
    lococor_code = resolve_record_value(record, "LOCOCOR")
    idade_code = resolve_record_value(record, "IDADE")
    parsed_date_of_death = parse_sim_date(date_of_death)
    parsed_date_of_birth = parse_sim_date(date_of_birth)

    transformed.pop("MUNIRES", None)
    transformed.pop("MUNIOCOR", None)
    transformed.pop("DATAOBITO", None)
    transformed.pop("DATANASC", None)

    transformed["CODMUNRES"] = municipality_residence
    transformed["CODMUNOCOR"] = municipality_occurrence
    transformed["DTOBITO_BRUTO"] = date_of_death
    transformed["DTNASC_BRUTO"] = date_of_birth
    transformed["SEXO_COD"] = sexo_code
    transformed["RACACOR_COD"] = racacor_code
    transformed["LOCOCOR_COD"] = lococor_code
    transformed["IDADE_COD"] = idade_code

    transformed["DTOBITO"] = parsed_date_of_death
    transformed["DTNASC"] = parsed_date_of_birth
    transformed["SEXO"] = map_code(sexo_code, SEXO_MAP)
    transformed["RACACOR"] = map_code(racacor_code, RACACOR_MAP)
    transformed["LOCOCOR"] = map_code(lococor_code, LOCOCOR_MAP)
    transformed["IDADE_ANOS"] = decode_sim_age_to_years(idade_code)
    transformed["ANO_OBITO"] = extract_year_from_iso_date(parsed_date_of_death)
    transformed["ANO_NASC"] = extract_year_from_iso_date(parsed_date_of_birth)
    transformed["DATA_OBITO_VALIDA"] = parsed_date_of_death is not None
    transformed["DATA_NASC_VALIDA"] = parsed_date_of_birth is not None
    transformed["SC_RESIDENCIA"] = is_sc_municipality_code(municipality_residence)
    transformed["SC_OCORRENCIA"] = is_sc_municipality_code(municipality_occurrence)
    return transformed


def should_retry_http_error(exc: HTTPError) -> bool:
    return exc.code == 429 or 500 <= exc.code < 600


def fetch_api_payload(
    api_url: str,
    offset: int,
    limit: int,
    timeout: int,
    retries: int,
    retry_wait: int,
) -> tuple[dict[str, Any], str]:
    params = {"offset": offset, "limit": limit}
    query = urlencode(params)
    url = f"{api_url}?{query}"

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "PyAnalytics-SIM/1.0",
        },
    )

    attempts = retries + 1
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                raw_bytes = response.read()
            payload_text = raw_bytes.decode("utf-8")
            return json.loads(payload_text), payload_text
        except HTTPError as exc:
            last_error = exc
            if not should_retry_http_error(exc) or attempt == attempts:
                raise
        except (URLError, SocketTimeout, TimeoutError) as exc:
            last_error = exc
            if attempt == attempts:
                raise

        print(
            f"[aviso] Falha ao buscar offset={offset} na tentativa "
            f"{attempt}/{attempts}: {last_error}. Nova tentativa em "
            f"{retry_wait}s.",
            file=sys.stderr,
        )
        if retry_wait:
            sleep(retry_wait)

    assert last_error is not None
    raise last_error


def extract_records_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("sim")
    if not isinstance(rows, list):
        raise ValueError("Resposta da API invalida: chave 'sim' ausente ou nao-lista.")
    return [uppercase_keys(row) for row in rows]


def detect_csv_encoding_and_dialect(input_path: Path) -> tuple[str, csv.Dialect | csv.excel]:
    sample_bytes = input_path.read_bytes()[:65536]
    encodings = ("utf-8-sig", "utf-8", "latin-1", "cp1252")
    sample_text = ""
    selected_encoding = "utf-8-sig"

    def can_decode_entire_file(encoding: str) -> bool:
        try:
            with input_path.open("r", encoding=encoding, newline="") as handle:
                while handle.read(1024 * 1024):
                    pass
            return True
        except UnicodeDecodeError:
            return False

    for encoding in encodings:
        try:
            sample_text = sample_bytes.decode(encoding)
            selected_encoding = encoding
            break
        except UnicodeDecodeError:
            continue

    if selected_encoding in ("utf-8-sig", "utf-8") and not can_decode_entire_file(selected_encoding):
        selected_encoding = "latin-1"
        sample_text = sample_bytes.decode(selected_encoding)

    try:
        dialect = csv.Sniffer().sniff(sample_text, delimiters=";,|\t")
    except csv.Error:
        delimiter = ";" if sample_text.count(";") >= sample_text.count(",") else ","
        dialect = csv.excel()
        dialect.delimiter = delimiter

    return selected_encoding, dialect


def iter_csv_records(input_path: Path) -> Any:
    encoding, dialect = detect_csv_encoding_and_dialect(input_path)
    with input_path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, dialect=dialect)
        for row in reader:
            yield uppercase_keys(dict(row))


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_rows_to_csv(
    output_path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str],
    write_header: bool,
) -> int:
    ensure_parent_dir(output_path)
    with output_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def build_fieldnames(records: list[dict[str, Any]]) -> list[str]:
    source_columns: list[str] = []
    seen: set[str] = set()

    for record in records:
        for column in record.keys():
            if column not in seen:
                source_columns.append(column)
                seen.add(column)

    for derived in DERIVED_COLUMNS:
        if derived not in seen:
            source_columns.append(derived)

    return source_columns


def process_records(
    records: list[dict[str, Any]],
    sc_scope: str,
) -> list[dict[str, Any]]:
    processed: list[dict[str, Any]] = []
    for record in records:
        if not keep_sc_record(record, sc_scope):
            continue
        processed.append(transform_record(record))
    return processed


def save_raw_payload(raw_dir: Path | None, offset: int, payload_text: str) -> None:
    if raw_dir is None:
        return

    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / f"sim_api_offset_{offset:06d}.json"
    target.write_text(payload_text, encoding="utf-8")


def default_state_file(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.state.json")


def read_existing_fieldnames(output_path: Path) -> list[str] | None:
    if not output_path.exists() or output_path.stat().st_size == 0:
        return None

    with output_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return None

    return header or None


def load_state(state_path: Path) -> dict[str, Any] | None:
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(
    state_path: Path,
    *,
    api_url: str,
    output_path: Path,
    limit: int,
    sc_scope: str,
    next_offset: int,
    rows_seen: int,
    rows_kept: int,
    rows_written: int,
    fieldnames: list[str] | None,
    finished: bool,
) -> None:
    ensure_parent_dir(state_path)
    payload = {
        "api_url": api_url,
        "output": str(output_path),
        "limit": limit,
        "sc_scope": sc_scope,
        "next_offset": next_offset,
        "rows_seen": rows_seen,
        "rows_kept": rows_kept,
        "rows_written": rows_written,
        "fieldnames": fieldnames,
        "finished": finished,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    state_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def reset_outputs(output_path: Path, state_path: Path) -> None:
    if output_path.exists():
        output_path.unlink()
    if state_path.exists():
        state_path.unlink()


def extract_year_token(path: Path) -> str:
    match = re.search(r"(19|20)\d{2}", path.stem)
    if match:
        return match.group(0)
    return path.stem


def build_local_output_name(path: Path) -> str:
    year_token = extract_year_token(path)
    return f"sim_sc_{year_token}.csv"


def list_local_csv_files(input_path: Path | None, input_dir: Path | None) -> list[Path]:
    if input_path is not None:
        return [input_path]
    if input_dir is None:
        return []

    candidates = sorted(
        path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".csv"
    )
    if not candidates:
        raise ValueError("Nenhum arquivo .csv foi encontrado em --input-dir.")
    return candidates


def write_empty_csv(output_path: Path) -> None:
    ensure_parent_dir(output_path)
    output_path.write_text("", encoding="utf-8")


def process_local_csv_file(
    input_path: Path,
    output_path: Path | None,
    sc_scope: str,
) -> LocalFileResult:
    rows_seen = 0
    rows_kept = 0
    rows_written = 0
    fieldnames: list[str] | None = None
    wrote_header = False

    if output_path is not None and output_path.exists():
        output_path.unlink()

    for record in iter_csv_records(input_path):
        rows_seen += 1
        if not keep_sc_record(record, sc_scope):
            continue

        transformed = transform_record(record)
        rows_kept += 1

        if output_path is not None:
            if fieldnames is None:
                fieldnames = build_fieldnames([transformed])
            rows_written += write_rows_to_csv(
                output_path=output_path,
                rows=[transformed],
                fieldnames=fieldnames,
                write_header=not wrote_header,
            )
            wrote_header = True

    if output_path is not None and not wrote_header:
        write_empty_csv(output_path)

    return LocalFileResult(
        source=input_path,
        output=output_path,
        rows_seen=rows_seen,
        rows_kept=rows_kept,
        rows_written=rows_written,
    )


def collect_csv_fieldnames(csv_path: Path) -> list[str]:
    encoding, dialect = detect_csv_encoding_and_dialect(csv_path)
    with csv_path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.reader(handle, dialect=dialect)
        try:
            header = next(reader)
        except StopIteration:
            return []
    return header


def merge_csv_files(
    input_paths: list[Path],
    output_path: Path,
) -> int:
    fieldnames: list[str] = []
    seen: set[str] = set()

    for path in input_paths:
        if not path.exists() or path.stat().st_size == 0:
            continue
        for column in collect_csv_fieldnames(path):
            if column not in seen:
                fieldnames.append(column)
                seen.add(column)

    if not fieldnames:
        write_empty_csv(output_path)
        return 0

    if output_path.exists():
        output_path.unlink()

    rows_written = 0
    ensure_parent_dir(output_path)
    with output_path.open("a", encoding="utf-8", newline="") as out_handle:
        writer = csv.DictWriter(out_handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for path in input_paths:
            if not path.exists() or path.stat().st_size == 0:
                continue
            with path.open("r", encoding="utf-8-sig", newline="") as in_handle:
                reader = csv.DictReader(in_handle)
                for row in reader:
                    writer.writerow(row)
                    rows_written += 1

    return rows_written


def process_local_sources(
    input_path: Path | None,
    input_dir: Path | None,
    output_path: Path,
    yearly_output_dir: Path | None,
    sc_scope: str,
) -> BatchResult:
    source_files = list_local_csv_files(input_path, input_dir)
    annual_outputs: list[Path] = []
    total_seen = 0
    total_kept = 0

    if input_dir is None:
        single_result = process_local_csv_file(
            input_path=source_files[0],
            output_path=output_path,
            sc_scope=sc_scope,
        )
        return BatchResult(
            rows_seen=single_result.rows_seen,
            rows_kept=single_result.rows_kept,
            rows_written=single_result.rows_written,
            next_offset=0,
        )

    assert yearly_output_dir is not None
    yearly_output_dir.mkdir(parents=True, exist_ok=True)

    for source_file in source_files:
        annual_output = yearly_output_dir / build_local_output_name(source_file)
        result = process_local_csv_file(
            input_path=source_file,
            output_path=annual_output,
            sc_scope=sc_scope,
        )
        total_seen += result.rows_seen
        total_kept += result.rows_kept
        annual_outputs.append(annual_output)

        print(
            f"[info] arquivo={source_file.name} lidos={result.rows_seen} "
            f"mantidos_sc={result.rows_kept} escritos={result.rows_written}",
            file=sys.stderr,
        )

    total_written = merge_csv_files(annual_outputs, output_path)

    return BatchResult(
        rows_seen=total_seen,
        rows_kept=total_kept,
        rows_written=total_written,
        next_offset=0,
    )


def restore_progress(
    *,
    output_path: Path,
    state_path: Path,
    reset: bool,
    requested_offset: int,
    limit: int,
    api_url: str,
    sc_scope: str,
) -> tuple[int, int, int, int, list[str] | None, bool, bool]:
    if reset:
        reset_outputs(output_path, state_path)
        return requested_offset, 0, 0, 0, None, False, False

    state = load_state(state_path)
    if state is None:
        if output_path.exists() and output_path.stat().st_size > 0:
            print(
                "[aviso] CSV existente sem arquivo de estado. Reiniciando a coleta "
                "a partir do offset informado e sobrescrevendo o CSV.",
                file=sys.stderr,
            )
            output_path.unlink()
        return requested_offset, 0, 0, 0, None, False, False

    if state.get("finished"):
        print(
            "[info] Estado anterior indica processamento concluido. Use --reset "
            "para recomecar.",
            file=sys.stderr,
        )
        return (
            int(state["next_offset"]),
            int(state["rows_seen"]),
            int(state["rows_kept"]),
            int(state["rows_written"]),
            state.get("fieldnames"),
            bool(output_path.exists() and output_path.stat().st_size > 0),
            True,
        )

    if state.get("api_url") != api_url:
        raise ValueError("O arquivo de estado pertence a outra API.")
    if int(state.get("limit", limit)) != limit:
        raise ValueError("O arquivo de estado foi criado com outro valor de --limit.")
    if state.get("sc_scope") != sc_scope:
        raise ValueError(
            "O arquivo de estado foi criado com outra regra de filtragem de SC."
        )

    next_offset = int(state["next_offset"])
    if next_offset < requested_offset:
        next_offset = requested_offset

    fieldnames = state.get("fieldnames")
    if not fieldnames:
        fieldnames = read_existing_fieldnames(output_path)

    wrote_header = bool(output_path.exists() and output_path.stat().st_size > 0)
    return (
        next_offset,
        int(state["rows_seen"]),
        int(state["rows_kept"]),
        int(state["rows_written"]),
        fieldnames,
        wrote_header,
        False,
    )


def process_api(
    api_url: str,
    output_path: Path,
    raw_dir: Path | None,
    state_path: Path,
    limit: int,
    offset: int,
    max_pages: int | None,
    timeout: int,
    retries: int,
    retry_wait: int,
    reset: bool,
    sc_scope: str,
) -> BatchResult:
    (
        current_offset,
        total_seen,
        total_kept,
        total_written,
        fieldnames,
        wrote_header,
        already_finished,
    ) = restore_progress(
        output_path=output_path,
        state_path=state_path,
        reset=reset,
        requested_offset=offset,
        limit=limit,
        api_url=api_url,
        sc_scope=sc_scope,
    )

    if wrote_header and fieldnames is None:
        fieldnames = read_existing_fieldnames(output_path)
        if fieldnames is None:
            raise ValueError("Nao foi possivel recuperar o cabecalho do CSV existente.")

    if already_finished:
        return BatchResult(
            rows_seen=total_seen,
            rows_kept=total_kept,
            rows_written=total_written,
            next_offset=current_offset,
        )

    seen_hashes: set[str] = set()
    processed_pages = 0
    finished = False

    while max_pages is None or processed_pages < max_pages:
        payload, payload_text = fetch_api_payload(
            api_url=api_url,
            offset=current_offset,
            limit=limit,
            timeout=timeout,
            retries=retries,
            retry_wait=retry_wait,
        )
        payload_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
        if payload_hash in seen_hashes:
            print(
                f"[info] Resposta repetida detectada no offset {current_offset}. "
                "Interrompendo para evitar duplicacao.",
                file=sys.stderr,
            )
            finished = True
            break
        seen_hashes.add(payload_hash)

        save_raw_payload(raw_dir, current_offset, payload_text)
        records = extract_records_from_payload(payload)
        if not records:
            print(
                f"[info] Offset {current_offset} retornou lote vazio. Fim da coleta.",
                file=sys.stderr,
            )
            finished = True
            break

        total_seen += len(records)
        processed = process_records(records, sc_scope)
        total_kept += len(processed)

        if processed:
            if fieldnames is None:
                fieldnames = build_fieldnames(processed)
            total_written += write_rows_to_csv(
                output_path=output_path,
                rows=processed,
                fieldnames=fieldnames,
                write_header=not wrote_header,
            )
            wrote_header = True

        next_offset = current_offset + 1
        save_state(
            state_path,
            api_url=api_url,
            output_path=output_path,
            limit=limit,
            sc_scope=sc_scope,
            next_offset=next_offset,
            rows_seen=total_seen,
            rows_kept=total_kept,
            rows_written=total_written,
            fieldnames=fieldnames,
            finished=False,
        )

        print(
            f"[info] offset={current_offset} recebidos={len(records)} "
            f"mantidos_sc={len(processed)} escritos_total={total_written}",
            file=sys.stderr,
        )

        processed_pages += 1
        current_offset = next_offset

        if len(records) < limit:
            print(
                f"[info] Ultima pagina detectada em offset={current_offset - 1} "
                f"(lote com {len(records)} registros).",
                file=sys.stderr,
            )
            finished = True
            break

    if fieldnames is None:
        ensure_parent_dir(output_path)
        output_path.write_text("", encoding="utf-8")

    save_state(
        state_path,
        api_url=api_url,
        output_path=output_path,
        limit=limit,
        sc_scope=sc_scope,
        next_offset=current_offset,
        rows_seen=total_seen,
        rows_kept=total_kept,
        rows_written=total_written,
        fieldnames=fieldnames,
        finished=finished,
    )

    return BatchResult(
        rows_seen=total_seen,
        rows_kept=total_kept,
        rows_written=total_written,
        next_offset=current_offset,
    )


def main() -> int:
    try:
        args = parse_args()
    except ValueError as exc:
        print(f"[erro] {exc}", file=sys.stderr)
        return 1

    try:
        if args.input is not None or args.input_dir is not None:
            result = process_local_sources(
                input_path=args.input,
                input_dir=args.input_dir,
                output_path=args.output,
                yearly_output_dir=args.yearly_output_dir,
                sc_scope=args.sc_scope,
            )
            state_file = None
        else:
            state_file = args.state_file or default_state_file(args.output)
            result = process_api(
                api_url=args.api_url,
                output_path=args.output,
                raw_dir=args.raw_dir,
                state_path=state_file,
                limit=args.limit,
                offset=args.offset,
                max_pages=args.max_pages,
                timeout=args.timeout,
                retries=args.retries,
                retry_wait=args.retry_wait,
                reset=args.reset,
                sc_scope=args.sc_scope,
            )
    except (HTTPError, URLError, SocketTimeout, TimeoutError) as exc:
        print(f"[erro] Falha na requisicao HTTP: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - tratamento de CLI
        print(f"[erro] {exc}", file=sys.stderr)
        return 1

    print(
        f"Processamento concluido. registros_lidos={result.rows_seen} "
        f"registros_sc={result.rows_kept} registros_escritos={result.rows_written} "
        f"proximo_offset={result.next_offset} arquivo_saida={args.output}"
    )
    if state_file is not None:
        print(f"arquivo_estado={state_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
