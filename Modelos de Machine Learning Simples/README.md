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

2. Pré-processamento dos dados
* Normalização: Os pixels são convertidos de 0–255 para o intervalo [0,1], o que acelera a convergência do treinamento.
* Achatamento (Flatten): As imagens 2D são transformadas em vetores 1D de 784 features, pois a MLP espera entradas planas.
* One-hot encoding: Os rótulos (0–9) são convertidos para vetores binários de 10 posições, compatíveis com a função de perda categorical_crossentropy.

3. Construção do modelo MLP
Arquitetura sequencial com duas camadas ocultas densas, ativação ReLU, dropout para regularização e camada de saída softmax.

4. Compilação do modelo
Utilizamos o otimizador Adam, a função de perda categorical_crossentropy (adequada para classificação multiclasse) e a métrica accuracy.

5. Treinamento do modelo
Treinamos por 10 épocas, com batch size de 128 e 10% dos dados de treino separados para validação.
O histórico do treinamento (history) armazena os valores de loss e acurácia para cada época, tanto no treino quanto na validação.

6. Avaliação do modelo
Após o treinamento, avaliamos o desempenho no conjunto de teste (dados nunca vistos).

7. Previsões e visualização
Selecionamos uma imagem aleatória do conjunto de teste, exibimos o dígito e fazemos a predição com o modelo treinado.

## **Resultados**
- Acurácia final no conjunto de teste: 98,13%
- Curvas de aprendizado: Os gráficos de acurácia e loss (apresentados no notebook) mostram que o modelo converge de forma estável, sem sinais de overfitting significativo.

### **Exemplo de previsão**
A célula de visualização exibe uma imagem aleatória e a respectiva previsão do modelo, permitindo verificar acertos e possíveis erros.

### **Interpretação dos Gráficos**
- Os gráficos gerados ao final do notebook permitem analisar o comportamento do treinamento:
- Acurácia crescente ao longo das épocas indica aprendizado efetivo.
- Proximidade entre curvas de treino e validação sugere boa generalização (pouco overfitting).
- Queda consistente da loss confirma que o modelo está otimizando corretamente.

## **Tecnologias Utilizadas**
* Python 3.10+
* TensorFlow 2.x / Keras
* Matplotlib
* NumPy
* Google Colab (ambiente de execução)

### **Como Executar**
* Clone este repositório ou faça o download do arquivo .ipynb.
* Abra o notebook no Google Colab ou Jupyter.
* Execute as células em ordem sequencial.
* Certifique-se de ter as bibliotecas instaladas (tensorflow, matplotlib, numpy).

## **Conclusão e Próximos Passos**
O modelo MLP desenvolvido atingiu uma acurácia de 98,13% no conjunto de teste do MNIST, demonstrando ser eficaz para a tarefa de classificação de dígitos manuscritos. O uso de dropout contribuiu para evitar overfitting, como observado pelas curvas de aprendizado.

### **Sugestões para trabalhos futuros:**
- Substituir a MLP por uma Rede Neural Convolucional (CNN), que tende a obter desempenho ainda superior em dados de imagem.
- Realizar ajuste de hiperparâmetros (número de neurônios, taxas de dropout, learning rate) para buscar melhorias.
- Aplicar data augmentation para aumentar a robustez do modelo.
- Salvar e exportar o modelo treinado para uso em aplicações reais.
