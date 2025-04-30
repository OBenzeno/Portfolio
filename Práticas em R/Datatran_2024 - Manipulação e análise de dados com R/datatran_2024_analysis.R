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

colSums(is.na(dados))  # Contagem de NAs por coluna

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

# Verificar estrutura dos dados
glimpse(dados_limpos)

## 5. Cálculos Probabilísticos

# Distribuição de Acidentes por Estado
estado_acidentes <- dados_limpos %>%
  group_by(uf) %>%
  summarise(total_acidentes = n()) %>% 
  mutate(estado_acidentes_prob = (total_acidentes / sum(total_acidentes)) * 100)

# Agrupar por fase do dia
acidentes_fase_dia <- dados_limpos %>% 
  group_by(fase_dia) %>% 
  summarise(total_fase_dia = n()) %>% 
  mutate(fase_dia_prob = (total_fase_dia / sum(total_fase_dia)) * 100)

# Distribuição de Acidentes por Condição Meteorológica
clima_acidentes <- dados_limpos %>%
  group_by(condicao_metereologica) %>%
  summarise(total_condicao_metereologica = n()) %>% 
  mutate(condicao_metereologica_prob = (total_condicao_metereologica / sum(total_condicao_metereologica)) * 100)

# Tipos de acidentes predominantes
predominante_acidentes <- dados_limpos %>% 
  group_by(tipo_acidente) %>% 
  summarise(total_tipo_acidente = n()) %>% 
  mutate(tipo_acidente_prob = (total_tipo_acidente / sum(total_tipo_acidente)) * 100)

# Causas de acidentes predominantes
causa_acidentes <- dados_limpos %>% 
  group_by(causa_acidente) %>% 
  summarise(total_causa_acidente = n()) %>% 
  mutate(causa_acidente_prob = (total_causa_acidente / sum(total_causa_acidente)) * 100)

# Qual o dia com maior risco de acidentes?
risco_dia <- dados_limpos %>% 
  group_by(dia_semana) %>% 
  summarise(total_dia_semana = n()) %>% 
  mutate(dia_semana_prob = (total_dia_semana / sum(total_dia_semana)) * 100)

## Probabilidade Condicional
#Qual a probabilidade de um acidente ser fatal ("com vítima fatal"), dado que ocorreu à noite?

# Filtrar acidentes
acidentes_noite <- dados_limpos %>% filter(fase_dia == "Plena Noite")
acidentes_dia <- dados_limpos %>% filter(fase_dia == "Pleno dia")

# Calcular P(Fatal | Noite)
prob_fatal_noite <- mean(acidentes_noite$classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE) * 100
cat("Probabilidade de acidente fatal à noite:", round(prob_fatal_noite, 2), "%")

#Qual a probabilidade de um acidente ser fatal ("com vítima fatal"), dado que ocorreu durante o dia?

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

# Principais Causas de Acidentes e sua Predominância
causa_acidentes %>%
  arrange(desc(causa_acidente_prob)) %>%
  slice_head(n = 10) %>%
  ggplot(aes(x = reorder(causa_acidente, -causa_acidente_prob), y = causa_acidente_prob, fill = causa_acidente)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.1f%%", causa_acidente_prob)), hjust = -0.2, size = 3) + 
  scale_y_continuous(labels = percent_format(scale = 1)) +  
  labs(title = "Distribuição Percentual das Principais Causas de Acidentes (%)", x = "Causa de Acidente", y = "Probabilidade (%)", caption="Fonte: Elaborado pelo autor, 2025") +
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
  
## 7. Específicos - Projeto Integrado

# Filtrar apenas acidentes fatais  
acidentes_fatais <- dados_limpos %>%  
  filter(classificacao_acidente == "Com Vitimas Fatais")  

# Análise das causas mais comuns em acidentes fatais  
causas_fatais <- acidentes_fatais %>%  
  count(causa_acidente, sort = TRUE) %>%  
  mutate(probabilidade = (n / nrow(acidentes_fatais)) * 100)  

# Top 5 causas  
head(causas_fatais, 5)  

# Cruzar com fase do dia  
acidentes_fatais %>%  
  group_by(fase_dia) %>%  
  summarise(total = n()) %>%  
  mutate(prob_fase = total / sum(total) * 100)  

# Agrupar por condição meteorológica e calcular taxa de fatalidade  
clima_risco <- dados_limpos %>%  
  group_by(condicao_metereologica) %>%  
  summarise(  
    total = n(),  
    fatalidades = sum(classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE),  
    taxa_fatalidade = (fatalidades / total) * 100  
  ) %>%  
  arrange(desc(taxa_fatalidade))  

# Visualização  
ggplot(clima_risco, aes(x = reorder(condicao_metereologica, -taxa_fatalidade), y = taxa_fatalidade)) +  
  geom_col(fill = "firebrick") +  
  labs(title = "Taxa de Fatalidade por Condição Meteorológica", x = "Condição", y = "% de Acidentes Fatais") +  
  theme_minimal() +  
  coord_flip()  

# Criar categorias (1 veículo, 2-3, 4+)  
dados_veiculos <- dados_limpos %>%  
  mutate(categoria_veiculos = case_when(  
    veiculos == 1 ~ "1 veículo",  
    veiculos %in% 2:3 ~ "2-3 veículos",  
    veiculos >= 4 ~ "4+ veículos"  
  ))  

# Calcular gravidade por categoria  
gravidade_veiculos <- dados_veiculos %>%  
  group_by(categoria_veiculos) %>%  
  summarise(  
    media_mortos = mean(mortos, na.rm = TRUE),  
    media_feridos_graves = mean(feridos_graves, na.rm = TRUE)  
  )  

# Teste estatístico (ANOVA para diferenças entre grupos)  
summary(aov(mortos ~ categoria_veiculos, data = dados ))  

## 8. Frequência e Proporção

# Calcular frequência e proporção de cada tipo de acidente
frequencia_tipos <- dados_limpos %>%
  count(tipo_acidente, name = "total") %>%
  mutate(
    proporcao = (total / sum(total)) * 100,
    tipo_acidente = reorder(tipo_acidente, -total)  # Ordenar do mais comum
  )

# Top 5 tipos mais frequentes
top5_freq <- frequencia_tipos %>% 
  arrange(desc(proporcao)) %>% 
  head(5)

# Gráfico minimalista
ggplot(head(top5_freq, 5), 
       aes(x = reorder(tipo_acidente, proporcao), 
           y = proporcao, 
           fill = tipo_acidente)) +
  geom_col() +
  labs(x = "Tipo de Acidente", y = "Proporção (%)") + 
  scale_fill_viridis_d() +  # Escala de cores vibrantes
  coord_flip() +
  theme_minimal()+
  theme(legend.position = "none")

# Calcular proporção de fatalidades, feridos e sem vítimas
gravidade_acidentes <- dados_limpos %>%
  group_by(classificacao_acidente) %>%
  summarise(
    total = n(),
    proporcao = (total / nrow(dados)) * 100
  ) %>%
  arrange(desc(proporcao))

# Resultado
gravidade_acidentes

# Gráfico
ggplot(head(gravidade_acidentes, 5), 
       aes(x = reorder(classificacao_acidente, proporcao), 
           y = proporcao, 
           fill = classificacao_acidente)) +
  geom_col() +
  labs(x = "Classificação de Acidente", y = "Proporção (%)") + 
  scale_fill_viridis_d() +  # Escala de cores vibrantes
  coord_flip() +
  theme_minimal()+
  theme(legend.position = "none")

# Taxa de fatalidade por tipo de acidente
taxa_fatalidade <- dados_limpos %>%
  group_by(tipo_acidente) %>%
  summarise(
    total = n(),
    fatalidades = sum(classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE),
    taxa_fatalidade = (fatalidades / total) * 100
  ) %>%
  arrange(desc(taxa_fatalidade))

# Top 5 tipos com maior taxa de fatalidade
top5_fatal <- taxa_fatalidade %>% 
  arrange(desc(taxa_fatalidade)) %>% 
  head(5)

# Gráfico
ggplot(head(top5_fatal, 5), 
       aes(x = reorder(tipo_acidente, taxa_fatalidade), 
           y = taxa_fatalidade, 
           fill = tipo_acidente)) +
  geom_col() +
  labs(x = "Tipo de Acidente", y = "Taxa de Fatalidade (%)") + 
  scale_fill_viridis_d() +  # Escala de cores vibrantes
  coord_flip() +
  theme_minimal()+
  theme(legend.position = "none")

## 9. Análise Avançada de Gravidade e Fatores de Risco
# Relação entre Condições Meteorológicas e Gravidade
clima_gravidade <- dados_limpos %>%
  group_by(condicao_metereologica) %>%
  summarise(
    total = n(),
    fatal = sum(classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE),
    taxa_fatal = (fatal / total) * 100,
    .groups = 'drop'
  ) %>%
  arrange(desc(taxa_fatal))

top5_clima_grave <- clima_gravidade %>% 
  arrange(desc(taxa_fatal)) %>% 
  head(5)

# Gráfico
ggplot(head(top5_clima_grave, 5), 
       aes(x = reorder(condicao_metereologica, taxa_fatal), 
           y = taxa_fatal, 
           fill = condicao_metereologica)) +
  geom_col() +
  labs(x = "Condição Meteorológica", y = "Taxa de Fatalidade (%)") + 
  coord_flip() +
  theme_minimal()+
  theme(legend.position = "none")

# Influência do Horário e Tipo de Pista
# Horário vs Gravidade
horario_gravidade <- dados_limpos %>%
  group_by(fase_dia) %>%
  summarise(
    fatal_rate = mean(classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE) * 100,
    .groups = 'drop'
  )

#Gráfico
ggplot(horario_gravidade, aes(x = reorder(fase_dia, fatal_rate), y = fatal_rate, fill = fase_dia)) +
  geom_col() +
  labs(x = "Fase do Dia", y = "Taxa de Gravidade (%)") + 
  coord_flip() +
  theme_minimal()+
  theme(legend.position = "none")

# Tipo de pista vs Gravidade
pista_gravidade <- dados_limpos %>%
  group_by(tipo_pista) %>%
  summarise(
    fatal_rate = mean(classificacao_acidente == "Com Vitimas Fatais", na.rm = TRUE) * 100,
    .groups = 'drop'
  )

# Gráfico
ggplot(pista_gravidade, aes(x = tipo_pista, y = fatal_rate, fill = tipo_pista)) +
  geom_bar(stat = "identity", show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f%%", fatal_rate)), vjust = -0.5, size = 3.5) +
  labs(x = "Tipo de Pista", y = "Taxa (%)") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) 

# Resultados combinados
list(Horário = horario_gravidade, Pista = pista_gravidade)

## 10. Análise de Texto das Causas de Acidentes: 
# Criar um dataframe com as causas
causas <- dados_limpos %>%
  select(causa_acidente) %>%
  mutate(
    # Padronizar texto: minúsculas, remover pontuação
    causa_limpa = str_to_lower(causa_acidente) %>%
      str_remove_all("[[:punct:]]")
  )
# Tokenizar e contar palavras-chave
palavras_chave <- causas %>%
  unnest_tokens(word, causa_limpa) %>%
  count(word, sort = TRUE) %>%
  filter(nchar(word) > 3)  # Remover palavras muito curtas

# Visualizar top 10 palavras
head(palavras_chave, 10)

# Gráfico
palavras_chave %>%
  arrange(desc(n)) %>%
  slice_head(n = 10) %>%
  ggplot(aes(x = reorder(word, -n), y = n, fill = word)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%d", n)), hjust = -0.2, size = 3) + 
  labs(x = "Palavra-chave", y = "Total") +
  theme_minimal() +
  theme(legend.position = "none") + 
  coord_flip()

# Agrupamento Semântico das Causas
causas_agrupadas <- causas %>%  
  mutate(  
    categoria_causa = case_when(  
      str_detect(causa_acidente, "alcool|etilico") ~ "Álcool/Drogas",  
      str_detect(causa_acidente, "velocidade|incompativel") ~ "Velocidade Inadequada",  
      str_detect(causa_acidente, "sono|cansaco") ~ "Fadiga/Sono",  
      str_detect(causa_acidente, "distancia|frenagem") ~ "Distância Segura",  
      str_detect(causa_acidente, "sinalizacao|faixa") ~ "Falha de Sinalização",  
      TRUE ~ "Outras Causas"  
    )  
  )  

# Contagem por categoria  
contagem_causas <- causas_agrupadas %>%  
  count(categoria_causa, sort = TRUE)  

# Gráfico
ggplot(contagem_causas, aes(x=reorder(categoria_causa, -n), y=n, fill=categoria_causa)) +
  geom_bar(stat="identity") +
  geom_text(aes(label=n), vjust=-0.3) +
  labs(x="Categoria", y="Total") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle=45, hjust=1), legend.position = "none")

# Causas Associadas a Acidentes Fatais
causas_acidentes_fatais <- dados_limpos %>%
  mutate(
    categoria_causa = case_when(
      str_detect(causa_acidente, "alcool|etilico") ~ "Álcool/Drogas",
      str_detect(causa_acidente, "velocidade|incompativel") ~ "Velocidade Inadequada",
      str_detect(causa_acidente, "sono|cansaco") ~ "Fadiga/Sono",
      str_detect(causa_acidente, "distancia|frenagem") ~ "Distância Segura",
      str_detect(causa_acidente, "sinalizacao|faixa") ~ "Falha de Sinalização",
      TRUE ~ "Outras Causas"
    )
  ) %>%
  filter(classificacao_acidente == "Com Vitimas Fatais") %>%  
  count(categoria_causa, sort = TRUE) %>%  
  mutate(proporcao = n / sum(n) * 100)

# Visualizar resultado
head(causas_fatais, 5)

# Gráfico
ggplot(causas_acidentes_fatais, aes(x = categoria_causa, y = proporcao, fill = categoria_causa)) +
  geom_bar(stat = "identity", show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.1f%%", proporcao)), vjust = -0.5, size = 3.5) +
  labs(x = "Causa", y = "Proporção (%)") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) 
