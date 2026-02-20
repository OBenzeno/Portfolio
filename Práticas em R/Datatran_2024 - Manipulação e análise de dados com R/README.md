# Projeto de Integrado  e Estatística Para Análise de Dados Referente ao 3º Semestre do Curso Superior de Tecnologia - Ciência de Dados
---

# 🚗 Análise de Dados de Acidentes de Trânsito – 2024

![R](https://img.shields.io/badge/R-4.x-blue)
![tidyverse](https://img.shields.io/badge/tidyverse-2.0-green)
![Status](https://img.shields.io/badge/status-concluído-brightgreen)
![Licença](https://img.shields.io/badge/licença-MIT-lightgrey)

> Projeto de análise exploratória de dados (EDA) sobre acidentes de trânsito no Brasil utilizando o dataset do DATATRAN 2024. O objetivo é identificar padrões, calcular probabilidades, visualizar distribuições e extrair insights sobre fatores de risco e gravidade dos acidentes.

---

## 📖 Sobre o Projeto

Este repositório contém um script em R desenvolvido como parte de um projeto integrado da faculdade. A partir da base de dados pública do DATATRAN 2024, realizamos:

- Limpeza e padronização de variáveis categóricas (remoção de acentos, tratamento de caracteres especiais).
- Cálculo de probabilidades absolutas e condicionais.
- Visualizações com `ggplot2` para comunicar os resultados.
- Análise textual das causas de acidentes com `tidytext`.
- Identificação de fatores associados à fatalidade (condições meteorológicas, horário, tipo de pista, número de veículos, etc.).

**Observação:** O script original incluía um teste ANOVA, que foi removido para manter o foco exclusivamente em estatísticas descritivas e probabilísticas.

---

## 📂 Estrutura do Projeto

```
📁 analise-acidentes-datran
├── 📄 datatran2024.csv # Base de dados (não incluída no repositório)
├── 📄 datatran_2024_analysis.R # Código completo em R
├── 📄 project.Rproj
├── 📄 README.md # Documentação (este arquivo)
└── 📁 outputs # (Opcional) Gráficos gerados
```


> **Nota:** O arquivo `datatran2024.csv` deve ser baixado do site oficial do DATATRAN (ou da fonte disponibilizada) e colocado no mesmo diretório do script.

---

## 🛠️ Tecnologias e Pacotes Utilizados

- **R 4.x**
- **tidyverse** (dplyr, ggplot2, tidyr, purrr, etc.)
- **stringi** – remoção de acentos
- **scales** – formatação de porcentagens nos gráficos
- **tidytext** – tokenização e análise de texto
- **viridis** – paletas de cores para gráficos (opcional, mas usado)

Instale os pacotes necessários com:
```r
install.packages(c("tidyverse", "stringi", "scales", "tidytext", "viridis"))
```

# 🚀 Como Executar

1. Clone o repositório (ou baixe os arquivos).  
2. Coloque o arquivo `datatran2024.csv` na mesma pasta do script.  
3. Abra o **RStudio** e execute o script `script_analise.R` inteiro (ou linha a linha).  
4. Os resultados (tabelas e gráficos) serão exibidos no console e nas abas de **Plots** do RStudio.  

---

# 🔍 Etapas da Análise

## 1. Carregamento e exploração inicial
- Leitura do CSV com encoding `latin1`.  
- Visualização das primeiras linhas (`head`), resumo estatístico (`summary`) e estrutura (`str`).  
- Contagem de valores ausentes (`colSums(is.na(...))`).  

## 2. Limpeza e padronização
- Remoção de acentos e caracteres especiais das colunas categóricas (`dia_semana`, `causa_acidente`, etc.) utilizando a função `stri_trans_general` do pacote `stringi`.  

## 3. Probabilidades (distribuições)
- Agrupamentos por: UF, fase do dia, condição meteorológica, tipo de acidente, causa, dia da semana.  
- Cálculo das proporções percentuais.  

## 4. Probabilidade condicional
- Cálculo de `P(fatal | noite)` e `P(fatal | dia)`.  
- Comparação entre os dois períodos.  

## 5. Visualizações
- Gráficos de barras com `ggplot2` para todas as variáveis analisadas:  
  - Acidentes por estado  
  - Probabilidade por fase do dia  
  - Distribuição percentual por condição climática  
  - Tipos de acidente mais comuns  
  - Principais causas (top 10)  
  - Risco por dia da semana  
- Uso de `coord_flip()`, rótulos percentuais e temas minimalistas  

## 6. Análise específica de acidentes fatais
- Filtro apenas para acidentes com vítimas fatais  
- Causas mais frequentes em fatais  
- Cruzamento com fase do dia e condição meteorológica  
- Taxa de fatalidade por condição climática (gráfico)  
- Gravidade por categoria de número de veículos (média de mortos e feridos graves)  

## 7. Frequência e proporção
- Top 5 tipos de acidente (frequência e proporção)  
- Proporção de acidentes por classificação (fatais, feridos, sem vítimas)  
- Top 5 tipos com maior taxa de fatalidade  

## 8. Análise avançada de gravidade
- Relação entre condições meteorológicas e taxa de fatalidade  
- Influência do horário (fase do dia) na gravidade  
- Influência do tipo de pista na gravidade  

## 9. Análise de texto das causas
- Tokenização das causas de acidentes  
- Contagem das palavras-chave mais frequentes (excluindo palavras curtas)  
- Agrupamento semântico das causas em categorias (Álcool/Drogas, Velocidade Inadequada, Fadiga/Sono, etc.)  
- Análise das categorias de causas em acidentes fatais  

---

# 📊 Principais Resultados (Exemplos)
- **Acidentes por estado:** Os estados com maior número de registros são... (depende dos dados)  
- **Fase do dia:** A maioria dos acidentes ocorre durante o dia, mas a probabilidade de fatalidade é maior à noite  
- **Condições climáticas:** “Chuva” aparece como condição com maior taxa de fatalidade  
- **Causas mais comuns:** “Ausência de reação do condutor” e “Velocidade incompatível” lideram  
- **Palavras-chave em causas:** “velocidade”, “alcool”, “reação”, “sinalização” são termos recorrentes  
- **Acidentes fatais:** As principais causas em fatais são relacionadas a álcool e velocidade  

> Os valores exatos dependem do dataset; o script os calcula dinamicamente.

# 📈 Exemplos de Gráficos Gerados

| Gráfico | Descrição |
|---------|-----------|
| `acidentes_por_estado` | Número absoluto de acidentes por UF |
| `prob_fase_dia` | Probabilidade percentual de acidente em cada fase do dia |
| `clima_acidentes` | Distribuição dos acidentes por condição meteorológica |
| `top_causas` | Principais causas de acidentes (em porcentagem) |
| `taxa_fatalidade_clima` | Taxa de fatalidade (%) em cada condição climática |
| `nuvem_palavras` (não implementado, mas pode ser adicionado) | Word cloud das causas |

---

# 📝 Conclusão

A análise exploratória permitiu identificar padrões importantes sobre a ocorrência e gravidade dos acidentes de trânsito no Brasil. Fatores como período noturno, condições climáticas adversas e causas relacionadas a álcool ou velocidade estão associados a maiores taxas de fatalidade. Esses insights podem subsidiar políticas públicas de prevenção e campanhas educativas.  

O script é modular e pode ser facilmente adaptado para outros anos ou bases de dados similares.  

---

# 🤝 Como Contribuir

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests com melhorias, correções ou novas análises.  

1. Faça um fork do projeto  
2. Crie uma branch para sua feature:  
   ```bash
   git checkout -b feature/nova-analise
   ```

🤝 Como Contribuir

Contribuições são bem‑vindas! Sinta‑se à vontade para abrir issues ou pull requests com melhorias, correções ou novas análises.

1. Faça um fork do projeto.
2. Crie uma branch para sua feature:  `git checkout -b feature/nova-analise`
3. Commit suas mudanças:  `git commit -m 'Adiciona nova análise de ...'`
4. Push para a branch:  `git push origin feature/nova-analise`
5. Abra um Pull Request.

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
   
