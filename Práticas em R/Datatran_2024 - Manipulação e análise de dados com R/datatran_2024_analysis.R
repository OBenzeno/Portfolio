## 1. Acessar a Plataforma RStudio

# Instalar pacotes necessários
install.packages("tidyverse")
# Carregar bibliotecas
library(tidyverse)

## 2. Baixar e Carregar os Dados - Encoding como "latin1" para evitar erros de leitura de caracteres especiais como acentos e cedilhas
dados <- read.csv("datatran2024.csv", sep = ";", fileEncoding = "latin1", stringsAsFactors = FALSE)

head(dados) # Visualizar as primeiras linhas

## 3. Explorar os Dados

summary(dados) # Resumo estatístico das variáveis
str(dados) # Estrutura do dataset (tipo das variáveis)

## 4. Manipulação de Dados e Limpeza - Remoção de Caracteres Especiais

# Criar uma cópia do dataset original
dados_limpos <- dados  

# Lista das colunas a serem limpas
colunas_para_limpar <- c("dia_semana", "causa_acidente", "tipo_acidente", 
                         "classificacao_acidente", "condicao_metereologica", 
                         "tipo_pista", "tracado_via", "uso_solo")

# Criar uma função para remover acentos e substituir "ç"
dados_limpos[colunas_para_limpar] <- lapply(dados_limpos[colunas_para_limpar], function(x) {
  if (is.character(x)) stri_trans_general(x, "Latin-ASCII") else x
})

head(dados_limpos[colunas_para_limpar])

## 5. Cálculos Probabilísticos

# Estado com o maior número de acidentes
estado_acidentes <- dados_limpos %>%
  group_by(uf) %>%
  summarise(total_acidentes = n()) %>% 
  mutate(estado_acidentes_prob = (total_acidentes / sum(total_acidentes)) * 100)

# Agrupar por fase do dia
acidentes_fase_dia <- dados_limpos %>% 
  group_by(fase_dia) %>% 
  summarise(total_fase_dia = n()) %>% 
  mutate(fase_dia_prob = (total_fase_dia / sum(total_fase_dia)) * 100)

# Distribuição de Acidentes por Condição Climática
clima_acidentes <- dados_limpos %>%
  group_by(condicao_metereologica) %>%
  summarise(total_condicao_metereologica = n()) %>% 
  mutate(condicao_metereologica_prob = (total_condicao_metereologica / sum(total_condicao_metereologica)) * 100)

# Tipos de acidentes predominantes
predominante_acidentes <- dados_limpos %>% 
  group_by(tipo_acidente) %>% 
  summarise(total_tipo_acidente = n()) %>% 
  mutate(tipo_acidente_prob = (total_tipo_acidente / sum(total_tipo_acidente)) * 100)

# Qual o dia com maior risco de acidentes?
risco_dia <- dados_limpos %>% 
  group_by(dia_semana) %>% 
  summarise(total_dia_semana = n()) %>% 
  mutate(dia_semana_prob = (total_dia_semana / sum(total_dia_semana)) * 100)

## Probabilidade Condicional
#Qual a probabilidade de um acidente ser fatal ("com vítima fatal"), dado que ocorreu à noite?

# Filtrar acidentes à noite
acidentes_noite <- dados_limpos %>% filter(fase_dia == "Plena Noite")
acidentes_dia <- dados_limpos %>% filter(fase_dia == "Pleno dia")

# Calcular P(Fatal | Noite)
prob_fatal_noite <- mean(acidentes_noite$classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE) * 100
cat("Probabilidade de acidente fatal à noite:", round(prob_fatal_noite, 2), "%")

# Calcular P(Fatal | Dia)
prob_fatal_dia <- mean(acidentes_dia$classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE) * 100
cat("Probabilidade de acidente fatal durante o Dia:", round(prob_fatal_dia, 2), "%")

# Calcular P(Fatal Total)
prob_fatal <- prob_fatal_dia + prob_fatal_noite
cat("Probabilidade total de acidentes fatais (Dia + Noite):", round(prob_fatal, 2), "%")

## 6. Visualização dos Resultados com ggplot2

# Gráfico de Acidentes por Estado
ggplot(estado_acidentes, aes(x=reorder(uf, -total_acidentes), y=total_acidentes, fill=uf)) +
  geom_bar(stat="identity") +
  labs(title="Número de Acidentes por Estado", x="Estado", y="Total de Acidentes", caption=" Fonte: Elaborado pelo autor, 2025") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle=45, hjust=1), legend.position = "none")

# Como a fase do dia afeta a ocorrência de acidentes?
ggplot(acidentes_fase_dia, aes(x = fase_dia, y = fase_dia_prob, fill = fase_dia)) +
  geom_bar(stat = "identity", show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f%%", fase_dia_prob)), vjust = -0.5, size = 3.5) +
  labs(title = "Probabilidade de Acidentes por Fase do Dia (%)", x = "Fase do Dia", y = "Probabilidade (%)", caption=" Fonte: Elaborado pelo autor, 2025") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  

# Como a Condição Climática afeta a ocorrência de acidentes? 
ggplot(clima_acidentes, aes(x = reorder(condicao_metereologica, -condicao_metereologica_prob), y = condicao_metereologica_prob, fill = condicao_metereologica)) +
  geom_bar(stat = "identity", show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f%%", condicao_metereologica_prob)), hjust = -0.2, size = 3.5) + 
  scale_y_continuous(labels = percent_format(scale = 1)) +  
  labs(title = "Distribuição Percentual de Acidentes por Condição Climática", x = "Condição Climática", y = "Porcentagem de Acidentes (%)", caption=" Fonte: Elaborado pelo autor, 2025") +
  theme_minimal() +
  coord_flip() 

# Tipos de Acidentes Predominantes e suas Probabilidades
ggplot(predominante_acidentes, aes(x = reorder(tipo_acidente, -tipo_acidente_prob), y = tipo_acidente_prob, fill = tipo_acidente)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.1f%%", tipo_acidente_prob)), hjust = -0.2, size = 3) + 
  scale_y_continuous(labels = percent_format(scale = 1)) +  
  labs(title = "Distribuição Percentual dos Tipos de Acidentes (%)", x = "Tipo de Acidente", y = "Probabilidade (%)", caption=" Fonte: Elaborado pelo autor, 2025") +
  theme_minimal() +
  theme(legend.position = "none") + 
  coord_flip()  

# Risco de Acidentes por dia da semana
ggplot(risco_dia, aes(x = reorder(dia_semana, -dia_semana_prob), y = dia_semana_prob, fill = dia_semana)) +
  geom_bar(stat = "identity", show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f%%", dia_semana_prob)), hjust = 1.2, color = "white", size = 4, fontface = "bold") + 
  scale_y_continuous(labels = percent_format(scale = 1)) +  
  labs(title = "Probabilidade de Acidentes por Dia da Semana", x = "Dia da Semana", y = "Probabilidade (%)", caption=" Fonte: Elaborado pelo autor, 2025") +  
  theme_minimal() +
  coord_flip()
  
# Calcular Probabilidade de Acidente Fatal

