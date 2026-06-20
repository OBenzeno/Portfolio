import requests # Para fazer requisições HTTP à API
from requests.auth import HTTPBasicAuth # Para autenticação básica com a API
import time # Para lidar com limites de taxa da API
import os # Para acessar as variáveis de ambiente
import json # Para salvar e carregar o checkpoint
import pandas as pd # Para manipulação de dados e criação do DataFrame
from datetime import datetime # Para registrar o timestamp do checkpoint
from zoneinfo import ZoneInfo # Para lidar com fusos horários (se necessário)
from dotenv import load_dotenv # Para ler o arquivo .env
import re # Para limpeza de strings (opcional, dependendo do formato dos dados)
import unicodedata # Para normalização de texto (opcional, dependendo do formato dos dados)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
DNS = os.getenv("API_DNS") # DNS da API 
TOKEN = os.getenv("API_TOKEN_FILIAL1") # Token de autenticação da API

if not DNS or not TOKEN:
    raise ValueError("[ERRO] As variáveis de ambiente API_DNS e API_TOKEN devem ser definidas no arquivo .env.")

# Configurações da API
URL = os.getenv("END_POINT_DEBTORS") # URL da API para obter os dados de vendas

# Pretratamento específico para a coluna "saleitems" (ajuste conforme necessário com base no formato real dos dados)
def tratar_saleitens(valor):
    if valor is None or (not isinstance(valor, (list, dict)) and pd.isna(valor)):
        return valor
    texto = str(valor)
    # Normaliza unicode para ASCII removendo acentos
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', errors='ignore').decode('ascii')
    # Remove caracteres especiais
    texto = re.sub(r'[^a-zA-Z0-9\s,.:/]', '', texto).strip()
    return texto

# Checkpoint: carrega a última data de execução bem-sucedida para permitir cargas incrementais
CHECKPOINT_FILE = "checkpoint.json"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checkpoint(date_end):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_run": date_end}, f, indent=2)
    print(f"Checkpoint salvo: {date_end}")

checkpoint = load_checkpoint()
date_end = datetime.now(ZoneInfo("America/Fortaleza")).strftime("%Y-%m-%dT%H:%M:%S")
date_start = checkpoint.get("last_run") #or "2024-01-01T00:00:00" # Data inicial fixa para a primeira execução (pode ser ajustada conforme necessário)

if checkpoint.get("last_run"):
    print(f"[INFO] Carga incremental: buscando de {date_start} até {date_end}")
else:
    print(f"[INFO] Primeira execução: buscando de {date_start} até {date_end}")

# Paginação - a API suporta os parâmetros "take" (quantidade de registros por página) e "skip" (quantidade de registros a pular para a próxima página)
params = {
    "idBranch": 0,   # 0 = todas as filiais
    "take": 50,      # conforme endpoint_config.json
    "skip": 0,
}
# debtors não usa filtro de data (dateStartKey/dateEndKey = null no config)

all_sales = [] # Lista para armazenar todas as vendas

pagina = 1  # Contador de páginas

tentativas = 0 # Contador de tentativas para lidar com erros de servidor
max_tentativas = 5 # Número máximo de tentativas antes de desistir (pode ser ajustado conforme necessário)

# Loop para buscar os dados de vendas paginados
while True:
    print(f"[LOAD] Buscando registros de vendas a partir de: {params['skip']}") # Log para acompanhar o progresso da busca 
    print(f"[TRACE] Página: {pagina} - Tentativa: {tentativas + 1}/{max_tentativas}") # Log para acompanhar o número da página e tentativas

    try:
        response = requests.get( # Faz a requisição GET para a API
            URL, #type: ignore 
            params=params,
            auth=HTTPBasicAuth(DNS, TOKEN), # Autenticação básica usando o token
            timeout=30 # Tempo limite para a requisição
        ) 
        
        if response.status_code not in (200, 401, 429):
            response.raise_for_status()
        
        # Rate limit ou outros erros de conexão
        if response.status_code == 429:
            print(f"[ERRO] Rate limit atingido. Aguardando... {response.status_code}")
            time.sleep(10) # Espera um pouco antes de tentar novamente
            continue
        # Erro de autenticação        
        if response.status_code == 401:
            print(f"[ERRO] Erro de autenticação: Verifique seu token e DNS.")
            break
    
        # Outros erros de conexão
        if response.status_code != 200:
            print(f"[ERRO] Erro de conexão: {response.status_code} - {response.text}")
            time.sleep(10) # Espera um pouco antes de tentar novamente
            continue
    
        data = response.json()
    
        # debtors retorna {"results": [...]} conforme responseKey no config
        if isinstance(data, dict):
            sales = data.get("results", [])
        else:
            sales = data
        
        # Verifica se a resposta contém dados de vendas
        if not sales:
            print(f"[AVISO] Nenhum dado retornado. Finalizando a busca.")
            break
        
        all_sales.extend(sales) # Adiciona as vendas retornadas à lista de todas as vendas
        tentativas = 0 # Reseta o contador de tentativas após uma resposta bem-sucedida
        print(f"[REGISTRO] Total de vendas coletadas até o momento: {len(all_sales)}") # Log para acompanhar o número total de vendas coletadas
        
        # Paginação: Incrementa o parâmetro "skip" para buscar a próxima página de resultados
        if len(sales) < params["take"]:
            print(f"[INFO] Última página de resultados alcançada.")
            break
        
        params["skip"] += params["take"]
        pagina += 1
        time.sleep(1.8)
    
    # Tratamento específico pra 500 (deve vir antes do RequestException genérico)
    except requests.exceptions.HTTPError as e:
        tentativas += 1
        print(f"[ERRO SERVIDOR] Tentativa {tentativas}: {e}")

        if tentativas >= max_tentativas:
            print("[ERRO] Máximo de tentativas atingido.")
            break
        time.sleep(10)
        continue

    # Tratamento de exceções para lidar com erros de tempo limite (timeout) durante a requisição
    except requests.exceptions.Timeout:
        print(f"[ERRO] Timeout. Tentando novamente...")
        time.sleep(5)
        continue

    # Tratamento de exceções para lidar com outros erros de requisição, como problemas de conexão ou erros HTTP
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro na requisição: {e}")
        break
    
    # Tratamento de exceções para lidar com erros ao converter a resposta JSON
    except ValueError:
        print("[ERRO] Erro ao converter JSON.")
        break
    
    # Tratamento de exceções para lidar com interrupção do usuário (Ctrl+C) para permitir que o processo seja interrompido de forma segura e que o checkpoint seja salvo corretamente
    except KeyboardInterrupt:
        print("\n[INFO] Execução interrompida pelo usuário.")
        break

#Resultado final
print(f"[REGISTRO] Total de vendas coletadas: {len(all_sales)}") # Log para mostrar o total de vendas coletadas

if not all_sales:
    print("[AVISO] Nenhuma venda coletada. Verifique a API e as credenciais.")
    raise SystemExit(1)
    
# Normalização dos dados e criação do DataFrame
df_sales = pd.json_normalize(all_sales) # Normaliza os dados de vendas para criar um DataFrame
print(f"[INFO] DataFrame de vendas criado com sucesso.") # Log para indicar que o DataFrame foi criado com sucesso
print(df_sales.head()) # Exibe as primeiras linhas do DataFrame para verificação
    
# Criando um backup do dado bruto antes de qualquer transformação para garantir que o dado original esteja preservado para futuras análises ou auditorias
df_raw = df_sales.copy()  # Backup do dado bruto antes de qualquer transformação  
df_raw.to_csv("vendas_raw.csv", index=False, sep=";", encoding="utf-8")
print(f"[BACKUP] DataFrame raw criado com sucesso.") # Log para indicar que o DataFrame foi criado com sucesso

# Limpar e renomear as colunas do DataFrame para um formato mais limpo e consistente
df_sales.columns = [col.replace(" ", "_").lower() for col in df_sales.columns] # Renomeia as colunas para um formato mais limpo (sem espaços e em minúsculas)

# ------------------------------------------------------------------------------   

# DESATIVADO TEMPORARIAMENTE - A depender do formato real dos dados, pode ser necessário um tratamento específico para a coluna "saleitens" (ajuste conforme necessário com base no formato real dos dados)

# Tratamento específico para a coluna "saleitens" (ajuste conforme necessário com base no formato real dos dados)
#if "saleitens" in df_sales.columns:
#    df_sales["saleitens"] = df_sales["saleitens"].apply(tratar_saleitens)
#    print("[INFO] Coluna 'saleitens' tratada com sucesso.")
    
# ------------------------------------------------------------------------------   
    
# Exportação para CSV
arquivo = "vendas.csv" # Nome do arquivo CSV a ser criado

# Remover colunas desnecessárias (ajuste a lista de colunas a serem removidas com base na análise dos dados)
colunas_drop = ["coluna1", "coluna2", "coluna3"]  # definir após análise
df_sales.drop(columns=colunas_drop, inplace=True, errors="ignore")
    
# Verificação de duplicatas por ID (se a coluna "receivableId" existir) para evitar registros duplicados em cargas incrementais
if "receivableId" not in df_sales.columns:
    print("[AVISO] Coluna 'receivableId' não encontrada. Deduplicação por ID ignorada.")
else:     # camada extra de segurança com log)
    df_sales.drop_duplicates(subset=["receivableId"], inplace=True)
    print("[DROP] Registros duplicados por 'receivableId' removidos.")
    
    if os.path.exists(arquivo):
        df_old_ids = pd.read_csv(arquivo, sep=";", usecols=["receivableId"])
        qtd_antes = len(df_sales)
        df_sales = df_sales[~df_sales["receivableId"].isin(df_old_ids["receivableId"])]
        qtd_removidas = qtd_antes - len(df_sales)
        if qtd_removidas > 0:
            print(f"[DROP] {qtd_removidas} registros duplicados (mesmo ID) foram removidos antes da gravação.")
        else:
            print("[AVISO] Nenhuma duplicata por ID detectada.")
    else:
        print("[SEGURANÇA] Arquivo CSV não existe. Será criada uma nova base de dados.")

# Carga incremental: adiciona ao CSV existente. Carga completa: sobrescreve o arquivo
if date_start and os.path.exists(arquivo):
    df_sales.to_csv(arquivo, mode="a", header=False, index=False, sep=";", encoding="utf-8")
else:
    df_sales.to_csv(arquivo, index=False, sep=";", encoding="utf-8")

print(f"[INFO] Dados de vendas exportados para {arquivo} com sucesso.") # Log para indicar que os dados foram exportados com sucesso

# Salva o checkpoint após tudo concluído com sucesso
save_checkpoint(date_end)
