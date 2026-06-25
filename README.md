<div align="center">
  <img src="assets/IconPyAnalytics.png" alt="PyAnalytics" width="180"/>
</div>

# PyAnalytics

Projeto de extensão da **UFSC — Campus Araranguá** que desenvolve análises de dados a partir de **fontes públicas**, com foco na **região de Araranguá** e entorno.

O objetivo é apoiar membros da comunidade na exploração de informações relevantes e viabilizar **visualizações acessíveis ao público**, facilitando a compreensão de indicadores locais.

## Objetivos

- Coletar e organizar dados públicos de interesse regional
- Realizar tratamento e análise dos dados de forma reprodutível
- Produzir visualizações claras para divulgação à comunidade
- Manter o projeto aberto para contribuições da equipe e da comunidade acadêmica

## Estrutura do repositório

```
pyanalytics/
├── assets/              # Identidade visual do projeto
├── data/
│   ├── raw/             # Dados brutos (downloads e fontes originais)
│   └── processed/       # Dados tratados prontos para análise
├── notebooks/           # Notebooks exploratórios e relatórios
├── src/
│   └── data/            # Scripts de ingestão, limpeza e transformação
└── README.md
```

## Como começar

1. Clone o repositório:

```bash
git clone https://codigos.ufsc.br/pyanalytics/pyanalytics.git
cd pyanalytics
```

2. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências do projeto (quando disponíveis):

```bash
pip install -r requirements.txt
```

4. Coloque arquivos brutos em `data/raw/` e execute os scripts de `src/data/` para gerar dados em `data/processed/`.

## Fluxo de trabalho sugerido

1. **Obter dados** — salvar arquivos originais em `data/raw/`
2. **Processar** — aplicar limpeza e transformações via `src/data/`
3. **Explorar** — desenvolver análises em `notebooks/`
4. **Publicar** — gerar visualizações para divulgação à comunidade

## Contribuindo

Este é um projeto de extensão em construção. Para contribuir:

1. Crie uma branch a partir de `main`
2. Faça suas alterações seguindo a estrutura de pastas definida
3. Abra um merge request no GitLab descrevendo a mudança

## Instituição

**Universidade Federal de Santa Catarina (UFSC)**  
Campus Araranguá — Projeto de Extensão PyAnalytics

## Dúvidas

##### Tem alguma  padronização que devemos seguir nos nomes das branchs?
Coloquem o nome da atividade sem acentuação, por exemplo: saude_materna_infantil

##### Há diferentes opções para pegar os dados para a utilização, direto do csv no repositório ou por meio da API, podemos escolher qualquer uma?
Podem usar diretamente do CSV, já fizemos a limpeza para vocês seguirem para a próxima etapa de análise conforme as tarefas.

##### Quando for filtrar os dados que for utilizar na minha tarefa, devo salvar em um csv ou algo do tipo na parte dados processados ou algo assim?
Use os filtros no código em cima do CSV do repositório. Não precisa salvar o resultado. dos filtros, uma vez que ao filtrar o CSV novamente terá os mesmos resultados.
CSV inteiro > filtro dos dados que você vai usar > Dados na variavel > Gráficos.

##### Devo salvar os gráficos e análises (os scripts) na pasta de notebooks ou na pasta src/data? 
Salve em notebooks/Sprint_1_{nome da branch conforme a primeira pergunta}, no exemplo ficaria. Sprint_1_saude_materna_infantil

##### As semanas de desenvolvimento (atualmente 5) são para desenvolver por database ou por item da tarefa?
Cada tarefa é para uma sprint.
Vocês podem se organizar como preferirem, mas recomendamos dividir para as semanas os subtopicos e fazer fragmentado e ir validando, a organização é de vocês.

##### Vamos explorar e analisar outras bases de dados ou só essa?
Nessa sprint será somente essa.

##### O que eu escrevo na credencial para conectar meu computador ao repositório no gitlab importa (nunca usei o GitLab, apenas o GitHub)?
Você precisa gerar um token em "personal access tokens" nas configurações de usuário, para conseguir usar no terminal, mas também é possivel adicionar tudo direto pelo web se achar mais fácil, ou seja, criar no colab, baixar o .ipynb e enviar para a sua branch. (Vou fazer um vídeo explicando como usar das 2 formas neste final de semana).

##### Pode me explicar melhor a estrutura do repositório e o formato de entrega ao fim das semanas?
Pasta assets - contém arquivos para exibição no projeto (como png, pdf, etc)

Pasta data - está organizado os dados para serem utilizados, no momento tem apenas em precessed os dados do SIM.

Pasta dicionaries - contém dicionário para as bases de dados que vamos utilizar.

Pasta notebooks - conterá os códigos de vocês gerados durante as sprints.

Pasta src - Conterá os arquivos do Streamlit e refinamento inicial dos dados.

Readme - instruções gerais do projeto inclusive da estrutura das pastas e organização do projeto.

Issues board - Conterá as tarefas para cada sprint para vocês.

