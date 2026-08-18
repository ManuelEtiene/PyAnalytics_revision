"""Divide o CSV analítico do SIM em pedaços para o GitHub (<100 MB cada)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

MAX_MB = 40


def _destino_padrao() -> Path:
    """Pasta `data/processed/` na raiz do repositório StreamlitPA."""
    return Path(__file__).resolve().parents[1] / "data" / "processed"


def _origem_padrao() -> Path | None:
    """CSV completo no projeto PyAnalytics (irmão deste repo)."""
    candidato = (
        Path(__file__).resolve().parents[2]
        / "pyanalytics"
        / "data"
        / "processed"
        / "sim_sc_processado_analitico.csv"
    )
    return candidato if candidato.exists() else None


def split_csv(origem: Path, pasta: Path, max_mb: int = MAX_MB) -> list[Path]:
    """Quebra o CSV por linhas, fechando cada parte perto de `max_mb`."""
    max_bytes = max_mb * 1024 * 1024
    pasta.mkdir(parents=True, exist_ok=True)
    stem = origem.stem
    partes: list[Path] = []
    idx = 0
    arquivo = None
    escritor = None
    tamanho = 0

    with origem.open(encoding="utf-8", newline="") as entrada:
        leitor = csv.reader(entrada)
        cabecalho = next(leitor)

        for linha in leitor:
            if arquivo is None or tamanho >= max_bytes:
                if arquivo:
                    arquivo.close()
                idx += 1
                destino = pasta / f"{stem}.part{idx:03d}.csv"
                partes.append(destino)
                arquivo = destino.open("w", encoding="utf-8", newline="")
                escritor = csv.writer(arquivo)
                escritor.writerow(cabecalho)
                tamanho = arquivo.tell()

            escritor.writerow(linha)
            tamanho = arquivo.tell()

    if arquivo:
        arquivo.close()

    return partes


def main() -> int:
    """CLI: python scripts/split_sim_csv.py [origem] [destino]."""
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else _origem_padrao()
    pasta = Path(sys.argv[2]) if len(sys.argv) > 2 else _destino_padrao()

    if origem is None or not origem.exists():
        print("CSV de origem não encontrado.", file=sys.stderr)
        return 1

    partes = split_csv(origem, pasta)
    for parte in partes:
        mb = parte.stat().st_size / (1024 * 1024)
        print(f"{parte.name}: {mb:.1f} MB")
    print(f"Total: {len(partes)} partes em {pasta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
