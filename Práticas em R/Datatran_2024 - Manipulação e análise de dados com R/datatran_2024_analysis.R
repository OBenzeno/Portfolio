## 1. Acessar a Plataforma RStudio

# Instalar pacotes necessários
install.packages("tidyverse")
# Carregar bibliotecas
library(tidyverse)

## 2. Baixar e Carregar os Dados
dados <- read.csv("datatran2024.csv", sep = ";", fill = TRUE, check.names = FALSE)

head(dados) # Visualizar as primeiras linhas

## 3. Explorar os Dados

summary(dados) # Resumo estatístico das variáveis
str(dados) # Estrutura do dataset (tipo das variáveis)

## 4. Manipulação de Dados e Cálculos Probabilísticos

# Estado com o maior número de acidentes
estado_acidentes <- dados %>%
  group_by(uf) %>%
  summarise(total_acidentes = n()) %>%
  arrange(desc(total_acidentes))
print(estado_acidentes)

# Agrupar por fase do dia
acidentes_fase_dia <- dados %>% 
  group_by(fase_dia) %>% 
  summarise(total = n()) %>% 
  mutate(probabilidade = (total / sum(total)) * 100)

# Distribuição de Acidentes por Condição Climática
clima_acidentes <- dados %>%
  group_by(condicao_metereologica) %>%
  summarise(total_acidentes = n()) %>%
  arrange(desc(total_acidentes))
print(clima_acidentes)

# Probabilidade de um acidente ocorrer em condições climáticas claras
prob_clima_claro <- sum(dados$condicao_metereologica == "Céu Claro") / nrow(dados)
print(paste("Probabilidade de acidente ocorrer em condições climáticas claras:", round(prob_clima_claro * 100, 2), "%"))

# Tipos de acidentes predominantes
dados %>% 
  group_by(tipo_acidente) %>% 
  summarise(total = n()) %>% 
  arrange(desc(total)) %>% 
  head(5)

# Qual o dia com maior risco de acidentes?
dados %>% 
  group_by(dia_semana) %>% 
  summarise(
    total = n(),
    probabilidade = (n() / nrow(dados)) * 100

## Probabilidade Condicional
#Qual a probabilidade de um acidente ser fatal ("com vítima fatal"), dado que ocorreu à noite?

# Filtrar acidentes à noite
acidentes_noite <- dados %>% filter(fase_dia == "Plena Noite")
acidentes_dia <- dados %>% filter(fase_dia == "Pleno dia")

# Calcular P(Fatal | Noite)
prob_fatal_noite <- mean(acidentes_noite$classificacao_acidente == "Com Vítimas Fatais", na.rm = TRUE) * 100
cat("Probabilidade de acidente fatal à noite:", round(prob_fatal_noite, 2), "%")

# Calcular P(Fatal | Dia)
prob_fatal_dia <- mean(acidentes_dia$classificacao_acidente == "Com Vítimas Fatais", na.rm = TRUE) * 100
cat("Probabilidade de acidente fatal durante o Dia:", round(prob_fatal_dia, 2), "%")



## Risco Relativo (RR)
# Acidentes em rodovias ("BR") vs. vias urbanas ("URBANA")

# Contagem de acidentes em BRs e vias urbanas
total_br <- sum(dados$tipo_via == "BR", na.rm = TRUE)
total_urbana <- sum(dados$tipo_via == "URBANA", na.rm = TRUE)

# Acidentes fatais em cada tipo de via
fatais_br <- sum(dados$tipo_via == "BR" & dados$tipo_ocorrencia == "com vítima fatal", na.rm = TRUE)
fatais_urbana <- sum(dados$tipo_via == "URBANA" & dados$tipo_ocorrencia == "com vítima fatal", na.rm = TRUE)

# Risco Relativo (RR)
rr <- (fatais_br / total_br) / (fatais_urbana / total_urbana)
cat("Risco Relativo (BR vs. Urbana):", round(rr, 2))

## Modelo de Poisson (Eventos Raros)
# Qual a probabilidade de ocorrerem mais de 5 acidentes por hora em um estado?

# Supondo dados agregados por hora em SP
acidentes_sp_hora <- dados %>% 
  filter(uf == "SP") %>% 
  group_by(hora) %>% 
  summarise(n = n())

# Média de acidentes por hora
lambda <- mean(acidentes_sp_hora$n)

# P(X > 5) = 1 - P(X ≤ 5)
prob_mais_5 <- 1 - ppois(5, lambda)
cat("Probabilidade de >5 acidentes/hora em SP:", round(prob_mais_5, 4) * 100, "%")

## Teorema de Bayes
# Se um acidente foi fatal, qual a probabilidade de ter ocorrido com embriaguez?

# P(Embriaguez | Fatal) = P(Fatal | Embriaguez) * P(Embriaguez) / P(Fatal)
p_fatal_embriaguez <- mean(dados$tipo_ocorrencia[dados$embriaguez == "SIM"] == "com vítima fatal", na.rm = TRUE)
p_embriaguez <- mean(dados$embriaguez == "SIM", na.rm = TRUE)
p_fatal <- mean(dados$tipo_ocorrencia == "com vítima fatal", na.rm = TRUE)

p_embriaguez_fatal <- (p_fatal_embriaguez * p_embriaguez) / p_fatal
cat("Probabilidade de embriaguez dado acidente fatal:", round(p_embriaguez_fatal, 2) * 100, "%")


## 5 Visualização dos Resultados com ggplot2

# Gráfico de Acidentes por Estado
ggplot(estado_acidentes, aes(x=reorder(uf, -total_acidentes), y=total_acidentes, fill=uf)) +
  geom_bar(stat="identity") +
  labs(title="Número de Acidentes por Estado", x="Estado", y="Total de Acidentes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle=45, hjust=1))

# Como a Condição Climática afeta a ocorrência de acidentes? 
ggplot(clima_acidentes, aes(x=reorder(condicao_metereologica, -total_acidentes), y=total_acidentes, fill=condicao_metereologica)) +
  geom_bar(stat="identity") +
  coord_flip() +
  labs(title="Distribuição de Acidentes por Condição Climática", x="Condição Climática", y="Total de Acidentes") +
  theme_minimal()

# Como a fase do dia afeta a ocorrência de acidentes?
ggplot(fase_dia_prob, aes(x=fase_dia, y=probabilidade, fill=fase_dia)) +
  geom_bar(stat="identity") +
  labs(title="Probabilidade de Acidentes por Fase do Dia", x="Fase do Dia", y="Probabilidade") +
  theme_minimal()

# Gráfico de densidade para distribuição de acidentes por hora
ggplot(dados, aes(x = hora)) + 
  geom_density(fill = "red", alpha = 0.5) +
  labs(title = "Distribuição de Acidentes por Hora do Dia")

# Mapa de calor de risco por estado
estados <- read_state()
dados_estados <- left_join(estados, acidentes_por_estado, by = c("abbrev_state" = "uf"))
ggplot(dados_estados) +
  geom_sf(aes(fill = total)) +
  scale_fill_viridis_c("Total de Acidentes")






turnos_mais_acidentes <- dados %>%
  count(fase_dia, sort = TRUE) %>%  # Conta e ordena do maior para o menor
  rename(total_acidentes = n)       # Renomeia a coluna de contagem
print(turnos_mais_acidentes)

resumo <- dados %>% 
  group_by(dia_semana) %>% 
  summarise(total = n())
print(resumo)


