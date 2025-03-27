#  Passo 1: Instalando e Importando o NLTK
import nltk
nltk.download('punkt') # Baixa recursos necessários para tokenização

#  Passo 2: Tokenização de Texto

from nltk.tokenize import word_tokenize

texto = "O processamento de Linguagem Natural (NLP) é uma ára da inteligência artificial"

tokens = word_tokenize(texto)
print(tokens)

# Passo 3: Remoção de Stop Words
from nltk.corpus import stopwords
stop_words = set(stopwords.words('portuguese'))
filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
print(filtered_tokens)

# Passo 4: Análise de Frequência
from nltk.probability import FreqDist

freq_dist = FreqDist(filtered_tokens)
print(freq_dist.most_common(5)) # Exibe as 5 palavras mais frequentes