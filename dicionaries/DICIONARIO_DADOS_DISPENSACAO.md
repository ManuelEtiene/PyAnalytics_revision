# Dicionário de Dados - DISPENSAÇÃO

Este documento descreve o `dispensacao_analitico.csv`.
Cada linha representa uma movimentação de saída de material/medicamento.

## Colunas

| Coluna | Tipo esperado | Descrição |
|---|---|---|
| `competencia_inicial` | texto (`YYYYMM`) | Competência inicial informada no relatório de origem. |
| `competencia_final` | texto (`YYYYMM`) | Competência final informada no relatório de origem. Pode ficar vazia. |
| `ups_nome` | texto | Nome da unidade/UPS de dispensação. |
| `ups_codigo` | texto | Código da UPS no relatório original. |
| `bairro_nome` | texto | Nome do bairro associado ao registro. |
| `bairro_codigo` | texto | Código do bairro no relatório original. |
| `centro_custo_nome` | texto | Nome do centro de custo. |
| `centro_custo_codigo` | texto | Código do centro de custo no relatório original. Pode ficar vazio. |
| `material_nome` | texto | Nome completo do item, já com limpeza básica de texto. |
| `material_nome_base` | texto | Nome principal do item, usado como base para agrupamentos e cruzamentos. Ex.: `CLONAZEPAM`. |
| `material_descricao_complementar` | texto | Parte intermediária do nome do material. Costuma conter dosagem, concentração, volume ou descrição complementar. |
| `material_tipo` | texto | Forma/apresentação do item. Ex.: `COMPRIMIDO`, `FRASCO`, `UNIDADE`. |
| `classe_terapeutica` | texto | Classe terapêutica inferida a partir do arquivo complementar `DADOS_ABERTOS_MEDICAMENTOS.csv`. |
| `tipo_tratamento` | texto | Agrupamento mais amplo criado a partir da classe terapêutica. Ex.: `Saúde mental e neurologia`, `Infecções`, `Sistema digestivo`. |
| `material_codigo` | texto | Código do material no relatório original. |
| `data` | data (`YYYY-MM-DD`) | Data da saida do material. |
| `saida` | texto | Identificador da movimentação/saída no sistema de origem. |
| `usuario` | texto | Usuário registrado no relatório de origem. |
| `fabricante_codigo` | texto | Código do fabricante extraído da coluna original `fabricante`. |
| `fabricante_nome` | texto | Nome do fabricante extraído da coluna original `fabricante`. |
| `lote` | texto | Número do lote do item dispensado. |
| `numero_receita` | texto | Número da receita, quando informado no relatório. Pode ficar vazio. |
| `validade` | data (`YYYY-MM-DD`) | Data de validade do lote. Pode ficar vazia. |
| `quantidade` | inteiro | Quantidade dispensada na movimentação. |
| `custo_medio` | decimal | Custo médio unitário, em R$. |

## Observações

- O arquivo foi gerado a partir de relatórios paginados, então várias colunas foram reconstruídas a partir do contexto do relatório original.
- `classe_terapeutica` e `tipo_tratamento` são inferidos por correspondência com a base complementar. Nem todos os materiais terão classificação preenchida.
- Itens não medicamentosos, como agulhas e canetas, podem ter classificação terapêutica vazia ou menos precisa.
- `material_nome` foi mantido no arquivo para referência bruta, mesmo após a criação das colunas derivadas de material.
- Para análises por produto, prefira `material_nome_base`. Para análises mais detalhadas por apresentação, combine `material_nome_base`, `material_descricao_complementar` e `material_tipo`.
