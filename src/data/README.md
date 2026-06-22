## SIM via API

O script [`src/data/sim_pipeline.py`](src/data/sim_pipeline.py) foi ajustado para o endpoint paginado do SIM usando apenas `limit` e `offset`.

Exemplo de uso:

```bash
python src/data/sim_pipeline.py \
  --output data/processed/sim_sc_processado.csv \
  --limit 1000 \
  --offset 0
```

Comportamento do pipeline:

- consome a API em lotes paginados;
- filtra Santa Catarina durante a ingestão, antes de gravar no CSV;
- escreve o resultado de forma incremental, sem manter toda a base em memória;
- salva o progresso em `data/processed/sim_sc_processado.state.json`;
- retoma automaticamente do último `offset` salvo se a execução cair ou atingir timeout.

Opções úteis:

- `--timeout 1800` aumenta o tempo máximo de cada requisição para 30 minutos;
- `--max-pages N` limita quantas páginas serão processadas em uma execução;
- `--reset` descarta o CSV e o estado salvos para recomeçar do zero;
- `--raw-dir data/raw/sim_api` salva cada resposta bruta da API em JSON.

## SIM via CSV local

Quando os arquivos anuais já estiverem baixados, o mesmo script pode processar os CSVs localmente, filtrando SC durante a leitura.

Para um unico arquivo:

```bash
python src/data/sim_pipeline.py \
  --input data/raw/sim/DOSC2024.csv \
  --output data/processed/sim_sc_2024.csv
```

Para um diretório com vários anos:

```bash
python src/data/sim_pipeline.py \
  --input-dir data/raw/sim/anos \
  --yearly-output-dir data/processed/sim_por_ano \
  --output data/processed/sim_sc_processado.csv
```

Nesse modo:

- cada arquivo anual é processado separadamente;
- uma saida filtrada é gravada para cada ano em `--yearly-output-dir`;
- no final, o script gera um CSV consolidado em `--output`;
- o consolidado faz união de colunas por nome para lidar com variacões de schema entre anos.

## Pos-processamento de CSV ja gerado

Quando o CSV do SIM já foi gerado e você quer apenas complementar a normalização, sem rerodar a ingestão completa, use [`src/data/sim_postprocess_csv.py`](src/data/sim_postprocess_csv.py).

Exemplo de uso:

```bash
python src/data/sim_postprocess_csv.py \
  --input data/processed/sim_sc_processado.csv \
  --output data/processed/sim_sc_processado_v2.csv
```

O pós-processamento pode:

- preencher `CODMUNRES` e `CODMUNOCOR` a partir de `MUNIRES` e `MUNIOCOR`;
- preencher ou corrigir `DTOBITO` e `DTNASC` a partir das colunas brutas;
- adicionar `ANO_OBITO`, `ANO_NASC`, `DATA_OBITO_VALIDA`, `DATA_NASC_VALIDA`, `SC_RESIDENCIA` e `SC_OCORRENCIA`;
- remover colunas legadas redundantes como `MUNIRES`, `MUNIOCOR`, `DATAOBITO` e `DATANASC`.

Para manter as colunas legadas no arquivo final, use --keep-legacy-columns.

O parametro --mode analytic gera uma versao enxuta apenas com colunas confiaveis para análise, preservando o arquivo completo original como referência.