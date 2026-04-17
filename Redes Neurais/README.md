# 🌡️ Conversão Celsius → Fahrenheit com Redes Neurais

[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21.0-FF6F00?logo=tensorflow)](https://tensorflow.org)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Este projeto foi desenvolvido como atividade prática para a disciplina **Redes Neurais e Deep Learning**. O objetivo é criar um modelo preditivo usando **TensorFlow** e **Keras** que aprenda a converter temperaturas de Celsius para Fahrenheit a partir de exemplos, sem conhecer a fórmula matemática previamente.

## 📌 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Dados de Treinamento](#dados-de-treinamento)
- [Arquitetura do Modelo](#arquitetura-do-modelo)
- [Treinamento](#treinamento)
- [Resultados](#resultados)
- [Como Executar](#como-executar)
- [Estrutura do Notebook](#estrutura-do-notebook)
- [Licença](#licença)

## 🧠 Sobre o Projeto

No modelo tradicional de programação, converter Celsius para Fahrenheit é trivial: `F = C * 1.8 + 32`. Porém, este exercício simula um cenário de **Machine Learning supervisionado**:

- Não sabemos a fórmula de antemão.
- Fornecemos apenas pares de exemplo (Celsius, Fahrenheit).
- A rede neural **descobre** a relação através de ajustes sucessivos de pesos e vieses.

Isso demonstra como modelos de deep learning podem aprender mapeamentos complexos quando a relação matemática é desconhecida.

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**
- **TensorFlow 2.21.0** – construção e treinamento da rede neural
- **NumPy** – manipulação dos dados numéricos
- **Matplotlib** – visualização da curva de perda (loss)
- **Pandas** – exibição da tabela comparativa

## 📊 Dados de Treinamento

Foram utilizados os seguintes 7 pares de temperatura (Celsius → Fahrenheit):

| Celsius (°C) | Fahrenheit (°F) |
|--------------|----------------|
| -40          | -40             |
| -10          | 14              |
| 0            | 32              |
| 8            | 46.4            |
| 15           | 59              |
| 22           | 71.6            |
| 38           | 100             |

Estes dados são suficientes para o modelo aprender a relação linear, pois a rede possui apenas 2 parâmetros ajustáveis (peso e viés).

## 🏗️ Arquitetura do Modelo

O modelo utilizado é **extremamente simples**, composto por uma única camada densa:

```python
modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=[1]),  # entrada: valor em Celsius
    tf.keras.layers.Dense(units=1)     # saída: valor em Fahrenheit
])```


