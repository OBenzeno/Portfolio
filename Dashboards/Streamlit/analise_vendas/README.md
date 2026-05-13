<div align="center">

# Análise de Vendas — Dashboard Interativo

Dashboard analítico de vendas construído com **Streamlit** e **Plotly**, com navegação entre três páginas, filtros interativos e visualizações em tema escuro.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.24%2B-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

</div>

---

## Demonstração

> **Adicione aqui um GIF do dashboard em execução.**
> Sugestão: `![Demo](screenshots/demo.gif)`

---

## Páginas

### Visão Geral
<!-- Substitua pelo caminho do seu screenshot -->
![Visão Geral](screenshots/visao_geral.png)

### Performance
<!-- Substitua pelo caminho do seu screenshot -->
![Performance](screenshots/performance.png)

### Geografia
<!-- Substitua pelo caminho do seu screenshot -->
![Geografia](screenshots/geografia.png)

| # | Página | Visualizações |
|---|--------|---------------|
| 1 | **Visão Geral** | KPIs · Evolução Temporal · Top Categorias · Receita por Marca (Donut) · Top 10 Produtos |
| 2 | **Performance** | Margem por Categoria · Receita vs Custo vs Lucro por Marca · Treemap Categoria × Marca |
| 3 | **Geografia** | Mapa Coroplético Mundial · Top 15 Países · Receita por Continente |

---

## Funcionalidades

- **Filtros globais** — período (por ano ou intervalo personalizado), categoria e marca via checkboxes na sidebar
- **Filtro de continente** — pills interativos na página de Geografia
- **Série temporal com drill-down** — visualização anual com zoom para nível mensal via `tickformatstops`
- **KPI cards** — receita, lucro, margem, quantidade e clientes únicos, com variação percentual
- **Quebra de linha automática** — labels longas nos gráficos de barras quebram por palavra
- **Treemap** — paleta de cores mutada para melhor contraste em tema escuro
- **Mapa coroplético** — choropleth mundial com escala de cor e tooltip por país
- **Tema escuro customizado** — CSS injetado com animação de fade-in entre páginas
- **Sidebar estilizada** — ícones SVG + botões pill para navegação entre páginas

---

## Estrutura do Projeto

```
Análise de Vendas/
├── dashboard.py          # Entry point — configuração, filtros e roteamento
├── data.py               # Carregamento, cache e transformação dos dados
├── requirements.txt      # Dependências do projeto
├── sidebar.py            # Sidebar com navegação e filtros interativos
├── styles.py             # CSS global injetado via st.markdown
├── utils.py              # Constantes de tema, helpers e componentes reutilizáveis
├── data/
│   └── vendas.csv.gz     # Dataset compactado (descompacte antes de executar)
├── screenshots/
│   ├── demo.gif
│   ├── visao_geral.png
│   ├── performance.png
│   └── geografia.png
└── views/
    ├── geografia.py      # Página 3 — Geografia
    ├── performance.py    # Página 2 — Performance
    └── visao_geral.py    # Página 1 — Visão Geral
```

---

## Como Executar Localmente

**Pré-requisito:** Python 3.11+

```bash
# 1. Clone apenas esta pasta (sparse checkout)
git clone --filter=blob:none --sparse https://github.com/Obenzeno/Portfolio.git
cd Portfolio
git sparse-checkout set "Dashboards e Visualização de Dados/Streamlit/Análise de Vendas"

# 2. Acesse a pasta do projeto
cd "Dashboards e Visualização de Dados/Streamlit/Análise de Vendas"

# 3. (Opcional) Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute o dashboard
streamlit run dashboard.py
```

O dashboard abrirá automaticamente em `http://localhost:8501`.

---

## Dataset

| Atributo | Detalhe |
|----------|---------|
| Período | Jun/2017 – Ago/2019 |
| Registros | ~204 mil linhas |
| Arquivo | `data/vendas.csv.gz` (~2 MB compactado) |

**Colunas principais:**

| Coluna | Descrição |
|--------|-----------|
| `Data da Venda` | Data da transação |
| `Produto` | Nome do produto |
| `Categoria` | Categoria do produto |
| `Marca` | Marca do produto |
| `Localidade` | País e continente |
| `PrecoUnitario` | Preço de venda unitário |
| `Custo Unitário` | Custo unitário do produto |
| `Qtd. Vendida` | Quantidade vendida |
| `Nome Cliente` | Identificação do cliente |

---

## Deploy

Hospedado via **Streamlit Community Cloud** — acesse em: `[link do deploy]`
