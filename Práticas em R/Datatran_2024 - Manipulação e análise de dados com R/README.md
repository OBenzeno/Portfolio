# Projeto de Integrado  e Estatística Para Análise de Dados Referente ao 3º Semestre do Curso Superior de Tecnologia - Ciência de Dados
---

# Análise de Acidentes de Trânsito

![GitHub Last Commit](https://img.shields.io/github/last-commit/OBenzeno/analise-acidentes)
![R](https://img.shields.io/badge/R-4.3+-blue)

Análise exploratória de dados de acidentes de trânsito utilizando R e técnicas de data science.

## 📊 Relatório Online

**[👉 Acesse o Relatório Aqui](https://OBenzeno.github.io/analise-acidentes/)**

## 🎯 Objetivos

- Identificar padrões em acidentes de trânsito
- Calcular probabilidades e riscos
- Analisar fatores de gravidade

## 🛠️ Tecnologias

- R + Tidyverse
- R Markdown/Quarto
- GitHub Actions
- ggplot2

## 📈 Resultados Principais

1. **Fase do dia** com maior risco: Pleno Dia (62.3%)
2. **Condição meteorológica** mais perigosa: Céu Claro
3. **Taxa de fatalidade** geral: 2.1%

## 🚀 Como Executar

```r
# Instalar dependências
install.packages(c("tidyverse", "rmarkdown"))

# Gerar relatório
rmarkdown::render("analysis.Rmd")
