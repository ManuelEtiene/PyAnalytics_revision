# Dados processados do SIM

Arquivos em pedaços de ~40 MB para caber no GitHub:

- `sim_sc_processado_analitico.part001.csv`
- `sim_sc_processado_analitico.part002.csv`
- …

Para regenerar a partir do CSV completo:

```bash
python scripts/split_sim_csv.py
```

O app lê todas as partes em sequência (`data/load_sim.py`).
