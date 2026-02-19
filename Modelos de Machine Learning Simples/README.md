# **Classificador de Dígitos Manuscritos com MLP (MNIST)**
### Atividade prática de Ciência de Dados

<img 
    align="left" 
    alt="Python" 
    title="Python"
    width="85px" 
    style="padding-right: 120px;" 
    src="https://img.shields.io/badge/python-3+-blue.svg" 
/>

<img 
    align="left" 
    alt="Tensorflow" 
    title="Tensorflow"
    width="110px"
    style="padding-right: 120px;" 
    src="https://img.shields.io/badge/TensorFlow-2+-orange.svg" 
/>

<br>

Este repositório contém a implementação de uma Rede Neural Multilayer Perceptron (MLP) para a classificação de dígitos manuscritos, utilizando o clássico conjunto de dados MNIST. O projeto foi desenvolvido como parte de uma atividade prática de Ciência de Dados, com o objetivo de construir, treinar e avaliar um modelo de aprendizado profundo para reconhecimento de padrões em imagens.

---

## **Objetivo**
Desenvolver um sistema de reconhecimento de dígitos manuscritos (0 a 9) utilizando uma rede neural do tipo Multilayer Perceptron (MLP). O modelo será treinado e avaliado com o conjunto de dados MNIST, seguindo as etapas padrão de um pipeline de machine learning.

## **Sumário**
1. Importar bibliotecas e carregar os dados

2. Pré-processamento dos dados

3. Construção do modelo MLP

4. Compilação do modelo

5. Treinamento do modelo

6. Avaliação do modelo

7. Previsões e visualização

### **Checklist da Atividade**

* Resultados
* Interpretação dos Gráficos
* Tecnologias Utilizadas
* Como Executar
* Conclusão e Próximos Passos

---

## **Procedimentos**
1. Importar bibliotecas e carregar os dados
Importamos as bibliotecas essenciais (tensorflow, matplotlib) e carregamos o dataset MNIST, que já vem dividido em treino e teste.

import tensorflow as tf <br>
from tensorflow.keras.datasets import mnist <br>
from tensorflow.keras.utils import to_categorical <br>
import matplotlib.pyplot as plt

(X_train, y_train), (X_test, y_test) = mnist.load_data()
Observação:

X_train possui 60.000 imagens 28×28 em escala de cinza.

X_test possui 10.000 imagens.

2. Pré-processamento dos dados
Normalização: Os pixels são convertidos de 0–255 para o intervalo [0,1], o que acelera a convergência do treinamento.

Achatamento (Flatten): As imagens 2D são transformadas em vetores 1D de 784 features, pois a MLP espera entradas planas.

One-hot encoding: Os rótulos (0–9) são convertidos para vetores binários de 10 posições, compatíveis com a função de perda categorical_crossentropy.

python
# Normalização
X_train = X_train / 255.0
X_test = X_test / 255.0

# Flatten
X_train = X_train.reshape((X_train.shape[0], 28*28))
X_test = X_test.reshape((X_test.shape[0], 28*28))

# One-hot encoding
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)
3. Construção do modelo MLP
Arquitetura sequencial com duas camadas ocultas densas, ativação ReLU, dropout para regularização e camada de saída softmax.


