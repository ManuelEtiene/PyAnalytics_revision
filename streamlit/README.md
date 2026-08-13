# Portal Streamlit — PyAnalytics / Araranguá

Documentação do site e do código do dashboard público de saúde do **PyAnalytics** (UFSC — Campus Araranguá).

---

## O que é

Portal web em **Streamlit** que transforma dados públicos do **SIM** (Sistema de Informações sobre Mortalidade) em painéis legíveis para população, gestores e comunidade acadêmica.

Foco atual: **óbitos de residentes de Araranguá (SC)**.

| Item | Valor |
|---|---|
| Entrada | `streamlit/app.py` |
| Dados | `data/processed/sim_sc_processado_analitico.csv` |
| Filtro | `CODMUNRES` = `420140` (Araranguá) |
| Stack | Streamlit · Pandas · Plotly |

---

## Como rodar

Na **raiz do repositório**:

```bash
# Ambiente (recomendado)
python -m venv .venv
source .venv/bin/activate

# Dependências
pip install -r requirements.txt

# Subir o portal
streamlit run streamlit/app.py
```

Abre em [http://localhost:8501](http://localhost:8501).

**Pré-requisito:** o CSV do SIM em `data/processed/sim_sc_processado_analitico.csv`. Sem ele, as páginas de dados falham com mensagem clara.

---

## Mapa do site (páginas)

| URL | Página | Status |
|---|---|---|
| `/inicio` | Home — KPIs e atalhos | Pronto |
| `/sobre` | Sobre o PyAnalytics | Pronto |
| `/sim` | Hub da base SIM | Pronto |
| `/retrato` | Retrato da mortalidade no município | Pronto |
| `/evitavel` | Mortalidade evitável | Em breve |
| `/materna` | Saúde materna e infantil | Em breve |
| `/onde-morrem` | Onde as pessoas morrem | Em breve |
| `/violentas` | Mortes violentas | Em breve |

Navegação nativa do Streamlit fica **oculta**. O usuário usa:

- **Header** — menu, atalhos, busca, tema
- **Drawer** — menu lateral (hambúrguer)
- **Combobox de busca** — filtra e abre a página

---

## Interface (UX)

### Header (fixo)

Ordem da esquerda para a direita:

1. **Menu** (☰) — abre/fecha o drawer  
2. **Info** — vai para Sobre  
3. **Início** — vai para a home  
4. **Logo + PyAnalytics**  
5. **Busca** (combobox) — digita, filtra, seleciona  
6. **Tema** — alterna claro ↔ escuro  

O header é **fixo na viewport** via CSS (não usa a barra nativa do Streamlit).

### Drawer (menu lateral)

Abre só com o hambúrguer (`st.session_state.menu_aberto`).

```
Geral
  · Início
  · Sobre PyAnalytics
Datasets
  ▸ SIM (Mortalidade)
      · Visão da base
      · Retrato...
      · (outros · em breve)
```

É um `st.container` com `position: fixed` — **não** é a `st.sidebar` nativa.

### Temas

| Estado | Onde |
|---|---|
| Claro | `styles/theme.css` |
| Escuro | `theme.css` + `styles/dark.css` (só se `tema_escuro=True`) |

Preferência fica em `st.session_state.tema_escuro`. Gráficos Plotly seguem o tema em `charts/theme.py` (`adaptar_tema`).

---

## Estrutura de pastas

```
streamlit/
├── app.py                 # Entrada: pages, header, drawer, footer
├── catalog.py             # Catálogo de páginas (NavItem)
├── navigation.py          # Registro para st.switch_page / page_link
├── assets/                # Logo local (fallback)
├── styles/
│   ├── theme.css          # Layout, header, drawer, cards (claro)
│   └── dark.css           # Overrides do modo escuro
├── components/            # Peças de UI reutilizáveis
│   ├── chrome.py          # Injeta CSS
│   ├── header.py          # Header + busca + tema
│   ├── drawer.py          # Menu lateral
│   ├── cards.py           # HTML dos cards (KPI, alerta, tópico)
│   ├── plot.py            # st.plotly_chart + insight
│   ├── footer.py
│   └── sidebar.py         # Reexport do drawer (compat)
├── views/                 # Uma view = uma página
│   ├── home.py
│   ├── sobre.py
│   ├── sim_hub.py
│   ├── retrato.py
│   ├── placeholder.py     # Páginas “em breve”
│   └── common.py          # load_or_stop, periodo
├── data/                  # Camada de dados
│   ├── paths.py           # Caminhos do CSV e do cache
│   ├── constants.py       # Códigos IBGE, colunas, etc.
│   ├── load_sim.py        # Leitura chunked + filtro Araranguá
│   ├── lookups.py         # CID-10, municípios, CBO, população
│   ├── decode.py          # Decodifica códigos → rótulos
│   ├── prepare_retrato.py # Preparação do Retrato
│   ├── kpis.py            # Números da Home
│   └── ranking.py         # Ranking entre municípios
├── charts/                # Figuras Plotly do Retrato
│   ├── theme.py           # Paleta + layout claro/escuro
│   ├── perfil.py
│   ├── cruzamentos.py
│   └── territorio.py
├── .streamlit/config.toml # Tema Streamlit (cores base)
└── .cache/                # Lookups baixados (gitignored)
```

---

## Fluxo de execução

```
app.py
  │
  ├─ set_page_config
  ├─ inject_theme()          # CSS claro (+ escuro se ativo)
  ├─ register(páginas)       # ids → st.Page
  ├─ st.navigation(... hidden)
  ├─ render_header()
  ├─ pg.run()                # view da URL atual
  ├─ render_footer()
  └─ render_drawer()         # só se menu_aberto
```

Cada view chama `render()`. Páginas com dados usam `views.common.load_or_stop()` → `data.load_sim.load_ararangua()` (cache Streamlit).

---

## Camada de dados

### CSV principal

| Campo | Detalhe |
|---|---|
| Arquivo | `data/processed/sim_sc_processado_analitico.csv` |
| Tamanho | ~centenas de MB (por isso leitura em chunks) |
| Função | `load_ararangua()` em `data/load_sim.py` |
| Cache | `@st.cache_data` |

### Lookups (cache local)

Baixados/gerados sob demanda em `streamlit/.cache/` (ignorado pelo Git):

| Arquivo | Uso |
|---|---|
| `cid10.csv` | Causas (CID-10) |
| `municipios.csv` | Nomes IBGE |
| `cbo.csv` | Ocupações |
| `populacao.csv` | População (taxas) |

### Módulos

| Módulo | Responsabilidade |
|---|---|
| `constants.py` | `COD_ARARANGUA`, colunas, chunk size |
| `decode.py` | Códigos → texto legível |
| `prepare_retrato.py` | Séries/tabelas do Retrato |
| `kpis.py` | Total, % hospital, causa principal |
| `ranking.py` | Posição de Araranguá em SC |

---

## Gráficos (Retrato)

Organizados por tema:

| Arquivo | Conteúdo |
|---|---|
| `perfil.py` | Ano, mês, faixa etária, sexo, raça, escolaridade, local, top causas |
| `cruzamentos.py` | Sexo×local, ocupação, heatmaps |
| `territorio.py` | Óbitos fora do município, deslocamento |
| `theme.py` | Cores PyAnalytics + adaptação dark |

Exibição sempre via `components.plot.plot(fig, insight)` — aplica `adaptar_tema` e esconde a toolbar do Plotly.

---

## Componentes de UI

| Arquivo | Função |
|---|---|
| `chrome.py` | Lê CSS e injeta com `st.markdown` |
| `header.py` | Header fixo, combobox, toggle de tema |
| `drawer.py` | Menu lateral fixo |
| `cards.py` | HTML (`glass-card`, `alert-card`, `topic-card`) |
| `plot.py` | Wrapper Plotly |
| `footer.py` | Rodapé |

**Convenção:** métodos curtos, uma responsabilidade; classes CSS com prefixo `pya-` ou `st-key-...` (keys do Streamlit).

---

## Catálogo e navegação

### `catalog.py`

`NavItem` descreve cada página (id, título, keywords, ícone, `ready`).

Funções úteis:

- `all_items()` — tudo navegável  
- `search_items(query)` — filtro por texto  
- `TOPICS` — subtópicos do SIM  

### `navigation.py`

`register(map)` no startup; `page("retrato")` devolve o `st.Page` para `st.page_link` / `st.switch_page`.

**Por que `url_path` único?** Todas as views usam `render` — sem `url_path`, o Streamlit colidia no pathname.

---

## Estilos CSS

### `theme.css`

- Esconde sidebar/header nativos do Streamlit  
- Header e drawer `position: fixed`  
- Largura da busca, ícones, marca  
- Cards, KPIs, tipografia (Inter + Hanken Grotesk)  

### `dark.css`

Injetado **somente** com tema escuro:

- Fundo `#12151a`, textos claros  
- Header, drawer, cards, busca  
- Textos SVG do Plotly (reforço)  

Variáveis úteis em `:root`:

```css
--pya-header-height
--pya-header-icon
--pya-header-logo
```

---

## Session state

| Chave | Uso |
|---|---|
| `menu_aberto` | Drawer aberto/fechado |
| `tema_escuro` | Modo escuro ativo |
| `nav_search` | Valor do combobox de busca |
| `_busca_aplicada` | Evita re-navegar o mesmo item |

---

## Como adicionar uma página nova

1. **Catálogo** — novo `NavItem` em `catalog.py` (`ready=True` quando houver conteúdo).  
2. **View** — arquivo em `views/` com `def render(): ...`.  
3. **App** — registrar em `_paginas()` com `url_path` único.  
4. **Menu** — se for tópico SIM, entra em `TOPICS` (já aparece no drawer).  
5. **Placeholder** — enquanto não houver dados, use `views/placeholder.py`.

Exemplo mínimo de view:

```python
def render() -> None:
    st.markdown("## Título")
    st.write("Conteúdo...")
```

---

## Como adicionar um gráfico ao Retrato

1. Função em `charts/perfil.py` (ou outro módulo) que retorna `(fig, insight)`.  
2. Use `apply_layout(fig, titulo)` de `charts/theme.py`.  
3. Chame `plot(fig, insight)` na view.

```python
from charts.theme import bar_vertical, apply_layout
from components.plot import plot

fig = bar_vertical(serie, "Óbitos por sexo")
plot(fig, "Homens e mulheres no período.")
```

---

## Configuração

| Arquivo | Papel |
|---|---|
| `streamlit/.streamlit/config.toml` | Cores base do Streamlit |
| `.streamlit/config.toml` (raiz) | Mesmo tema (cliente) |
| `requirements.txt` (raiz) | `streamlit`, `pandas`, `plotly` |

---

## Boas práticas do código

- Funções **pequenas** (< ~20 linhas quando possível)  
- Docstrings curtas em português  
- Views **não** carregam CSV direto — passam por `data/`  
- UI **não** calcula KPIs — passam por `kpis` / `prepare_*`  
- Preferir `st.container(key=...)` + CSS `.st-key-*` a gambiarras de DOM  
- Não usar `st.sidebar` (menu é o drawer customizado)  

---

## Problemas comuns

| Sintoma | Causa provável | Ação |
|---|---|---|
| Erro de CSV | Arquivo ausente | Colocar em `data/processed/` |
| Menu no meio da página | CSS do drawer não carregou | Hard refresh; checar `inject_theme` |
| Texto escuro no dark | Página sem `adaptar_tema` / CSS | Ver `plot.py` e `dark.css` |
| Import quebrado | Rodou de outra pasta | `streamlit run streamlit/app.py` na raiz |
| Pathname `render` duplicado | Falta `url_path` | Definir `url_path` único em `app.py` |

---

## Glossário

| Termo | Significado |
|---|---|
| SIM | Sistema de Informações sobre Mortalidade (DATASUS) |
| CODMUNRES | Código IBGE do município de residência |
| Retrato | Análise geral do perfil dos óbitos |
| Drawer | Painel lateral fixo (menu do hambúrguer) |
| NavItem | Entrada do catálogo de navegação |

---

## Manutenção rápida

```bash
# Rodar
streamlit run streamlit/app.py

# Limpar cache de dados do Streamlit (se mudar o CSV)
# (menu do app → Clear cache) ou apagar streamlit/.cache/
```

Projeto de extensão **UFSC Araranguá — PyAnalytics**.  
Dados públicos; código pensado para leitura e contribuição.
