import requests # Para fazer requisições HTTP à API
from requests.auth import HTTPBasicAuth 
import time # Para lidar com limites de taxa da API
import os 
import pandas as pd 
from datetime import datetime # Para registrar o timestamp do checkpoint
from zoneinfo import ZoneInfo 
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
DNS = os.getenv("API_DNS")
TOKEN = os.getenv("API_TOKEN") 

if not DNS or not TOKEN:
    raise ValueError("As variáveis de ambiente API_DNS e API_TOKEN devem ser definidas no arquivo .env.")

# Configurações da API
API_URL = os.getenv("API_URL") # URL da API para obter os dados de vendas

# Paginação - A API pode retornar um número limitado de registros por requisição, então usamos "take" para definir quantos registros queremos e "skip" para pular os registros já obtidos
params = {
    "idBranch": "null", # Filtrar por ID de filial (0 para todas as filiais)
    "take": 50, # Número de registros a serem retornados por requisição
    "skip": 0,   # Número de registros a serem pulados (para paginação)
    "dateSaleStart": "2026-01-01T00:00:00", # Data de início para filtrar as vendas (opcional)
    "dateSaleEnd": datetime.now(ZoneInfo("America/Fortaleza")).strftime("%Y-%m-%dT%H:%M:%S") # Data de fim para filtrar as vendas (opcional)
    }

all_sales = [] # Lista para armazenar todas as vendas

# Loop para buscar os dados de vendas paginados
while True:
    print(f"Buscando registros de vendas a partir de: {params['skip']}") # Log para acompanhar o progresso da busca 
        
    try:
        response = requests.get( # Faz a requisição GET para a API
            API_URL,
            params=params,
            auth=HTTPBasicAuth(DNS, TOKEN), # Autenticação básica usando o token
            timeout=30 # Tempo limite para a requisição
        ) 
        
        # Rate limit ou outros erros de conexão
        if response.status_code == 429:
            print(f"Rate limit atingido. Aguardando... {response.status_code}")
            time.sleep(10) # Espera um pouco antes de tentar novamente
            continue
        # Erro de autenticação        
        if response.status_code == 401:
            print("Erro de autenticação: Verifique seu token e DNS.")
            break
    
        # Outros erros de conexão
        if response.status_code != 200:
            print(f"Erro de conexão: {response.status_code} - {response.text}")
            time.sleep(10) # Espera um pouco antes de tentar novamente
            continue
    
        data = response.json()
    
        # Ajuste caso venha objetos
        if isinstance(data, dict):
            sales = data.get("data", [])
        else:
            sales = data
        
        # Verifica se a resposta contém dados de vendas
        if not sales:
            print("Nenhum dado retornado. Finalizando a busca.")
            break
        
        all_sales.extend(sales) # Adiciona as vendas retornadas à lista de todas as vendas
        print(f"Total de vendas coletadas até agora: {len(all_sales)}") # Log para acompanhar o número total de vendas coletadas
        
        # Paginação: Incrementa o parâmetro "skip" para buscar a próxima página de resultados
        if len(sales) < params["take"]:
            print("Última página de resultados alcançada.")
            break
        
        params["skip"] += params["take"]
        time.sleep(1.8)
    
    # Tratamento de exceções para lidar com erros de tempo limite (timeout) durante a requisição
    except requests.exceptions.Timeout:
        print("Timeout. Tentando novamente...")
        time.sleep(5)
        continue

    # Tratamento de exceções para lidar com outros erros de requisição, como problemas de conexão ou erros HTTP
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        break
    
    # Tratamento de exceções para lidar com erros ao converter a resposta JSON
    except ValueError:
        print("Erro ao converter JSON.")
        break

#Resultado final
print(f"Total de vendas coletadas: {len(all_sales)}") # Log para mostrar o total de vendas coletadas

if not all_sales:
    print("Nenhuma venda coletada. Verifique a API e as credenciais.")
    exit()
    
# Normalização dos dados e criação do DataFrame
df_sales = pd.json_normalize(all_sales) # Normaliza os dados de vendas para criar um DataFrame
print("DataFrame de vendas criado com sucesso.") # Log para indicar que o DataFrame foi criado com sucesso
print(df_sales.head()) # Exibe as primeiras linhas do DataFrame para verificação
    
#Limpar colunas desnecessárias
df_sales.columns = [col.replace(" ", "_").lower() for col in df_sales.columns] # Renomeia as colunas para um formato mais limpo (sem espaços e em minúsculas)

# Exportar para CSV
arquivo = "sales.csv" # Nome do arquivo CSV a ser criado
df_sales.to_csv(arquivo, index=False, sep=";", encoding="utf-8") # Exporta o DataFrame para um arquivo

print(f"Dados de vendas exportados para {arquivo} com sucesso.") # Log para indicar que os dados foram exportados com sucesso
