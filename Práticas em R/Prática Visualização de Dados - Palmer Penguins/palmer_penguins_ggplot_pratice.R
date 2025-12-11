# ==============================================================================
# ANÁLISE DE PINGUINS PALMER - SCRIPT R COMPLETO
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. CARREGAMENTO DE BIBLIOTECAS
# ------------------------------------------------------------------------------
library(ggplot2)
library(palmerpenguins)

# ------------------------------------------------------------------------------
# 2. EXPLORAÇÃO INICIAL DOS DADOS
# ------------------------------------------------------------------------------
# Visualizar estrutura dos dados
str(penguins)

# Ver dimensões do dataset
cat("Dimensões do conjunto de dados:\n")
dim(penguins)

# Visualizar primeiras linhas
cat("\nPrimeiras 6 linhas:\n")
head(penguins)

# Resumo estatístico
cat("\nResumo estatístico:\n")
summary(penguins)

# Visualizar dados em uma nova janela (se disponível)
# View(penguins)

# ------------------------------------------------------------------------------
# 3. VISUALIZAÇÕES BÁSICAS
# ------------------------------------------------------------------------------

# Gráfico 1: Comprimento da nadadeira vs Massa corporal
plot1 <- ggplot(data = penguins) +
  geom_point(mapping = aes(x = flipper_length_mm, 
                           y = body_mass_g, 
                           shape = species, 
                           color = species)) +
  labs(title = "Relação entre Comprimento da Nadadeira e Massa Corporal",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

print(plot1)

# Gráfico 2: Comprimento vs Profundidade do bico
plot2 <- ggplot(data = penguins) +
  geom_point(mapping = aes(x = bill_length_mm, 
                           y = bill_depth_mm, 
                           shape = species, 
                           color = species)) +
  labs(title = "Relação entre Comprimento e Profundidade do Bico",
       x = "Comprimento do bico (mm)",
       y = "Profundidade do bico (mm)")

print(plot2)

# ------------------------------------------------------------------------------
# 4. VISUALIZAÇÕES COM MÚLTIPLAS CAMADAS
# ------------------------------------------------------------------------------

# Gráfico 3: Suavização com pontos sobrepostos
plot3 <- ggplot(data = penguins) +
  geom_smooth(mapping = aes(x = flipper_length_mm, y = body_mass_g)) +
  geom_point(mapping = aes(x = flipper_length_mm, 
                           y = body_mass_g, 
                           shape = species, 
                           color = species)) +
  labs(title = "Relação Nadadeira-Massa com Suavização",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

print(plot3)

# ------------------------------------------------------------------------------
# 5. GRÁFICOS COM FACETAS
# ------------------------------------------------------------------------------

# Gráfico 4: Facetas por espécie
plot4 <- ggplot(data = penguins, aes(x = flipper_length_mm, y = body_mass_g)) +
  geom_point(aes(shape = species, color = species)) +
  facet_wrap(~species) +
  labs(title = "Relação Nadadeira-Massa por Espécie",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

print(plot4)

# Gráfico 5: Facetas por espécie (versão simplificada)
plot5 <- ggplot(data = penguins, aes(x = flipper_length_mm, y = body_mass_g)) +
  geom_point(aes(color = species)) +
  facet_wrap(~species) +
  labs(title = "Relação Nadadeira-Massa por Espécie (cores apenas)",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

print(plot5)

# Gráfico 6: Facetas por sexo e espécie (grade)
plot6 <- ggplot(data = penguins) +
  geom_point(mapping = aes(x = flipper_length_mm, 
                           y = body_mass_g, 
                           shape = species, 
                           color = species)) +
  facet_grid(sex ~ species) +
  labs(title = "Relação Nadadeira-Massa por Sexo e Espécie",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

print(plot6)

# Gráfico 7: Facetas apenas por sexo
plot7 <- ggplot(data = penguins) +
  geom_point(mapping = aes(x = flipper_length_mm, 
                           y = body_mass_g, 
                           shape = species, 
                           color = species)) +
  facet_grid(~sex) +
  labs(title = "Relação Nadadeira-Massa por Sexo",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

print(plot7)

# ------------------------------------------------------------------------------
# 6. GRÁFICOS COM ANOTAÇÕES E FORMATAÇÃO
# ------------------------------------------------------------------------------

# Gráfico 8: Com anotação personalizada
plot8 <- ggplot(data = penguins) +
  geom_smooth(mapping = aes(x = flipper_length_mm, y = body_mass_g)) +
  geom_point(mapping = aes(x = flipper_length_mm, 
                           y = body_mass_g, 
                           shape = species, 
                           color = species)) +
  labs(title = "Pinguins Palmer: Massa Corporal vs Comprimento da Nadadeira",
       subtitle = "Amostra de Três Espécies de Pinguins",
       caption = "Dados coletados pela Dra. Kristen Gorman",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)") +
  annotate("text", x = 220, y = 3500, 
           label = "Os Gentoos são os maiores", 
           color = "Purple",
           fontface = "bold", 
           size = 3.5, 
           angle = 25)

print(plot8)

# Gráfico 9: Salvando gráfico em objeto e modificando
p_base <- ggplot(data = penguins) +
  geom_smooth(mapping = aes(x = flipper_length_mm, y = body_mass_g)) +
  geom_point(mapping = aes(x = flipper_length_mm, 
                           y = body_mass_g, 
                           shape = species, 
                           color = species)) +
  labs(title = "Pinguins Palmer: Massa Corporal vs Comprimento da Nadadeira",
       caption = "Dados coletados pela Dra. Kristen Gorman",
       x = "Comprimento da nadadeira (mm)",
       y = "Massa corporal (g)")

# Versão 1: Com anotação
plot9_v1 <- p_base + 
  annotate("text", x = 220, y = 3500, 
           label = "Os Gentoos são os maiores",
           fontface = "italic",
           size = 3.5)

print(plot9_v1)

# Versão 2: Com tema diferente
plot9_v2 <- p_base +
  theme_minimal() +
  theme(legend.position = "bottom")

print(plot9_v2)

# ------------------------------------------------------------------------------
# 7. EXPORTAÇÃO DOS GRÁFICOS (OPCIONAL)
# ------------------------------------------------------------------------------
# Descomente para exportar os gráficos

# # Criar diretório para exportação
# if (!dir.exists("plots")) {
#   dir.create("plots")
# }
# 
# # Exportar gráficos como PNG
# ggsave("plots/plot1_nadadeira_massa.png", plot1, width = 8, height = 6, dpi = 300)
# ggsave("plots/plot2_bico.png", plot2, width = 8, height = 6, dpi = 300)
# ggsave("plots/plot8_com_anotacao.png", plot8, width = 10, height = 7, dpi = 300)

# ------------------------------------------------------------------------------
# 8. ANÁLISE ADICIONAL (OPCIONAL)
# ------------------------------------------------------------------------------
cat("\n=== ANÁLISE ESTATÍSTICA BÁSICA ===\n")

# Contagem por espécie
cat("\nContagem por espécie:\n")
table(penguins$species)

# Contagem por sexo
cat("\nContagem por sexo:\n")
table(penguins$sex)

# Médias por espécie
cat("\nMédia do comprimento da nadadeira por espécie:\n")
tapply(penguins$flipper_length_mm, penguins$species, mean, na.rm = TRUE)

cat("\nMédia da massa corporal por espécie:\n")
tapply(penguins$body_mass_g, penguins$species, mean, na.rm = TRUE)

# ------------------------------------------------------------------------------
# 9. GRÁFICO ADICIONAL: BOXPLOT POR ESPÉCIE
# ------------------------------------------------------------------------------
plot_boxplot <- ggplot(data = penguins, aes(x = species, y = body_mass_g, fill = species)) +
  geom_boxplot(alpha = 0.7) +
  labs(title = "Distribuição da Massa Corporal por Espécie",
       x = "Espécie",
       y = "Massa corporal (g)") +
  theme_minimal()

print(plot_boxplot)

# ------------------------------------------------------------------------------
# 10. MENSAGEM FINAL
# ------------------------------------------------------------------------------
cat("\n===========================================\n")
cat("SCRIPT EXECUTADO COM SUCESSO!\n")
cat("Foram criados", 11, "gráficos de análise exploratória.\n")
cat("===========================================\n")

# Limpar objetos temporários (opcional)
# rm(plot1, plot2, plot3, plot4, plot5, plot6, plot7, plot8, p_base, plot9_v1, plot9_v2, plot_boxplot)
