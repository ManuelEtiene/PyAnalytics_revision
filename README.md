<p align="center">
  <img src="assets/IconPyAnalytics.png" alt="PyAnalytics" width="180"/>
</p>

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
