# K-means Clustering - Machine Learning II

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.21%2B-blue?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1.3%2B-blue?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.4%2B-blue?logo=matplotlib&logoColor=white)
![Scikit--learn](https://img.shields.io/badge/Scikit--learn-1.0%2B-blue?logo=scikit-learn&logoColor=white)

**Autor:** Weslley Tiago Bitencourt de Andrade  
**Disciplina:** Machine Learning II  
**Objetivo:** Implementação e análise do algoritmo de agrupamento K-means em um conjunto de dados bidimensional, utilizando o método do cotovelo para determinar o número ideal de clusters.

## 📌 Descrição

Este repositório contém um notebook Jupyter (`kmeans_notebook.ipynb`) desenvolvido para a disciplina de Machine Learning II. O projeto explora o algoritmo **K-means** para segmentar um conjunto de 10 pontos no plano cartesiano, com os seguintes dados:

```python
x = [4, 5, 10, 4, 3, 11, 14, 6, 10, 12]
y = [21, 19, 24, 17, 16, 25, 24, 22, 21, 21]
```

## 🧠 Algoritmos e técnicas utilizadas

- K-means da biblioteca scikit-learn  
- Método do cotovelo (Elbow Method) para escolha do número de clusters  
- Visualização com matplotlib  
- Validação numérica dos resultados  

---

## 📊 Resultados principais

O método do cotovelo indicou **K = 2** como o número ideal de clusters.

Com **K = 2**, os pontos foram separados em dois grupos:

- **Cluster 1:** pontos com X ≤ 6 (valores baixos)  
- **Cluster 2:** pontos com X ≥ 10 (valores altos)  

**Centroides calculados:**

- Cluster 1: (4.40, 19.00)  
- Cluster 2: (11.40, 23.00)  

**Inércia final:** 56.4 (boa compactação dos clusters)

---

## 📈 Gráficos gerados

### Método do Cotovelo
O gráfico abaixo mostra a inércia para valores de K de 1 a 10. A queda acentuada até K=2 e a redução marginal a partir de K=3 indicam que K=2 é a escolha ideal.

![Método do Cotovelo](https://images/elbow_plot.png)

---

### Agrupamento com K = 2
A visualização dos dois clusters (vermelho e azul) e seus respectivos centroides (amarelo, formato "X") evidencia a separação clara dos dados.

![Clusters com K=2](https://images/clusters_k2.png)

---

## 🖥️ Como executar

### 1. Clone o repositório:

```bash
git clone https://github.com/OBenzeno/Portfolio.git
cd Portfolio/Machine Learning/kmeans_notebook.ipynb 
```
### 2. Instale as dependências:

```bash
pip install numpy pandas matplotlib scikit-learn
```

### 3. Execute o notebook:

```bash
### 3. Execute o notebook:
```

## 📁 Estrutura do repositório
```
.
├── kmeans_notebook.ipynb   # Notebook completo com código, gráficos e análise
├── images/                 # Pasta com os gráficos gerados
│   ├── elbow_plot.png      # Gráfico do método do cotovelo
│   └── clusters_k2.png     # Gráfico de dispersão dos clusters (K=2)
└── README.md               # Este arquivo
```

## 📝 Principais seções do notebook

- Importação de bibliotecas (inclui solução para warning do KMeans no Windows)
- Criação da base de dados e transformação em matriz de pontos
- Método do cotovelo – cálculo da inércia para K de 1 a 10 e plotagem
- Ajuste com K = 2 – visualização dos clusters e centroides
- Validação numérica – exibição de rótulos, contagem, centroides, inércia, tabela completa e médias por cluster
- Análise e discussão – interpretação dos resultados e aprendizados

## 📄 Licença
Este projeto é de uso acadêmico e está disponível para consulta e estudo.

## 🔗 Links
- [https://colab.research.google.com/kmeans_notebook.ipynb/ ](https://colab.research.google.com/drive/1syG2zp0zvqK6-VHEhDXK9MZYLRszqHcp?usp=sharing ) 
- [GitHub - kmeans_notebook.ipynb](https://github.com/OBenzeno/Portfolio/ /Redes%20Neurais/kmeans_notebook.ipynb)

Relatório gerado em conformidade com os requisitos da disciplina.
