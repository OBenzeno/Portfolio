# Análise de Vendas — Dashboard Interativo

Dashboard analítico de vendas construído com **Streamlit** e **Plotly**, com navegação entre três páginas, filtros interativos e visualizações responsivas em tema escuro.

---

## Visão Geral

| Página | Conteúdo |
|---|---|
| **Visão Geral** | KPIs, Evolução Temporal, Top Categorias, Receita por Marca (Donut), Top Produtos |
| **Performance** | Margem por Categoria, Receita vs Custo vs Lucro por Marca, Treemap Categoria × Marca |
| **Geografia** | Mapa Coroplético Mundial, Top 15 Países, Receita por Continente |

---

## Stack

- **Python 3.11+**
- **Streamlit 1.45+**
- **Plotly 5.x**
- **Pandas**

---

## Funcionalidades

- Filtro de período por ano ou intervalo personalizado
- Filtro de categoria e marca via checkboxes
- Filtro de continente via pills interativos
- Série temporal com drill-down por zoom (ano → mês)
- Labels com quebra de linha automática nos gráficos de barras
- Treemap com paleta de cores mutada para melhor contraste
- Tema escuro customizado com CSS e animação de fade-in entre páginas
- Sidebar com navegação estilizada (ícones SVG + botões pill)

---

## Estrutura do Projeto

```
dashboards_py/
├── dashboard.py          # Entry point / orquestrador
├── styles.py             # CSS global
├── data.py               # Carregamento e transformação dos dados
├── utils.py              # Constantes, helpers e componentes reutilizáveis
├── sidebar.py            # Sidebar com navegação e filtros
├── views/
│   ├── visao_geral.py    # Página 1 — Visão Geral
│   ├── performance.py    # Página 2 — Performance
│   └── geografia.py      # Página 3 — Geografia
└── data/
    └── vendas.csv.gz     # Dataset compactado (Jun/2017 – Ago/2019 · 203.888 registros)
```

---

## Como Executar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git

# 2. Acesse a pasta do projeto
cd "Dashboards e Visualização de Dados/Streamlit/Análise de Vendas"

# 3. Descompacte o dataset
gunzip data/vendas.csv.gz

# 4. Instale as dependências
pip install streamlit plotly pandas

# 5. Execute o dashboard
streamlit run dashboard.py
```

---

## Dataset

O arquivo `data/vendas.csv.gz` (compactado, ~2 MB) contém registros de vendas de **Jun/2017 a Ago/2019**. Descompacte com `gunzip data/vendas.csv.gz` antes de executar.

Colunas principais: `Data da Venda · Produto · Categoria · Marca · Localidade · PrecoUnitario · Custo Unitário · Qtd. Vendida · Nome Cliente`

---

## Deploy

Hospedado via **Streamlit Community Cloud**.
