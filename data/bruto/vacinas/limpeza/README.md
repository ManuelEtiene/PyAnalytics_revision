## 3. Observações Técnicas e Notas de Auditoria

1. **Manutenção de Registros Duplicados:**
   - O relatório nativo do G-MUS gera entradas individuais por vínculo de atendimento. Com a omissão/anonimização do identificador do paciente, imunizantes aplicados no mesmo lote e período geram registros identicamente estruturados.
   - **Opção de entrega:** As duplicidades exatas foram **mantidas na íntegra** para preservar o volume total de procedimentos/atendimentos registrados na fonte primária.

2. **Formato das Datas de Aplicação:**
   - As datas de aplicação apresentam-se no formato completo (`DD/MM/AAAA`) ou agrupadas por mês/ano (`MM/AAAA`), refletindo a transposição de dados históricos das carteirinhas físicas de vacinação para o sistema digital.

3. **Inconsistências Cadastrais Pontuais:**
   - No arquivo `bom_pastor.csv`, existem 3 registros com campos de dose/código de dose ausentes (Linhas 851, 1864 e 1990), decorrentes de divergências de preenchimento na origem do G-MUS.