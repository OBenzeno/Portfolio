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
import signal # Para lidar com interrupção do usuário (Ctrl+C)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
DNS = os.getenv("API_DNS") # DNS da API 
TOKEN = os.getenv("API_TOKEN") # Token de autenticação da API

if not DNS or not TOKEN:
    raise ValueError("[ERRO] As variáveis de ambiente API_DNS e API_TOKEN devem ser definidas no arquivo .env.")

# Configurações da API

# Mapeamento de endpoint para nome do arquivo de saída
ENDPOINT_ALIASES = {
    "sales": os.getenv("END_POINT_SALES"),
    "receivables": os.getenv("END_POINT_RECEIVABLES"),
    "membership": os.getenv("END_POINT_MEMBERSHIPS"),
    "prospects": os.getenv("END_POINT_PROSPECTS"),
}

# Log para mostrar os endpoints disponíveis para o usuário
print(f"[INFO] Endpoints disponíveis: {', '.join(ENDPOINT_ALIASES.keys())}")

# Solicita ao usuário que informe o endpoint para coleta de dados e valida a entrada
alias = input("[INPUT] Informe o endpoint para coleta de dados: ").strip().lower()
print(f"[REQUEST] Endpoint solicitado: {alias}")

if alias not in ENDPOINT_ALIASES:
    print(f"[ERRO] Alias '{alias}' não reconhecido.")
    print("[LOGOUT] Encerrando o processo. Verifique os aliases disponíveis e tente novamente.")
    raise SystemExit(1)

API_URL = ENDPOINT_ALIASES[alias] # URL da API para obter os dados de vendas

# Carrega as configurações específicas do endpoint a partir do arquivo JSON
with open("endpoint_config.json", "r") as f:
    ENDPOINT_PARAMS = json.load(f)

endpoint_cfg = ENDPOINT_PARAMS[alias]

# Extrai o caminho do endpoint para usar como parte do nome do arquivo de saída
endpoint_path = "/" + "/".join(API_URL.split("/")[3:]) # type: ignore
nome_base = alias                     # Nome do arquivo de saída
arquivo = f"{nome_base}.csv"
arquivo_raw = f"{nome_base}_raw.csv"

print(f"[INFO] Endpoint detectado: {endpoint_path}")
print(f"[INFO] Arquivos de saída: {arquivo} | {arquivo_raw}")

# Checkpoint: carrega a última data de execução bem-sucedida para permitir cargas incrementais
CHECKPOINT_FILE = f"checkpoint_{alias}.json"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checkpoint(date_end):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_run": date_end}, f, indent=2)
    print(f"Checkpoint salvo: {date_end}")

def encerrar_interrupt():
    print("\n[INTERRUPT] Execução interrompida pelo usuário.")
    print("[CHECKPOINT] Execução incompleta. Checkpoint não atualizado.")
    raise SystemExit(0)

def handle_interrupt(sig, frame):
    encerrar_interrupt()

signal.signal(signal.SIGINT, handle_interrupt)

checkpoint = load_checkpoint()
date_end = datetime.now(ZoneInfo("America/Fortaleza")).strftime("%Y-%m-%dT%H:%M:%S")
date_start = checkpoint.get("last_run") or "2024-01-01T00:00:00" # Data inicial fixa para a primeira execução (pode ser ajustada conforme necessário)

if checkpoint.get("last_run"):
    print(f"[CHECKPOINT] Carga incremental: buscando de {date_start} até {date_end}")
else:
    print(f"[INFO] Primeira execução: buscando de {date_start} até {date_end}")

# Paginação - a API suporta os parâmetros "take" (quantidade de registros por página) e "skip" (quantidade de registros a pular para a próxima página)
params = {
    "idBranch": endpoint_cfg["idBranch"],
    "take": endpoint_cfg["take"],
    "skip": endpoint_cfg["skip"],
}

if date_start and endpoint_cfg["dateStartKey"]:
    params[endpoint_cfg["dateStartKey"]] = date_start

if date_end and endpoint_cfg["dateEndKey"]:
    params[endpoint_cfg["dateEndKey"]] = date_end

all_data = [] # Lista para armazenar todas as vendas

pagina = 1  # Contador de páginas

tentativas = 0 # Contador de tentativas para lidar com erros de servidor
max_tentativas = 5 # Número máximo de tentativas antes de desistir (pode ser ajustado conforme necessário)

# Loop para buscar os dados de vendas paginados
while True:
    print(f"[LOAD] Buscando registros de {arquivo} a partir de: {params['skip']}") # Log para acompanhar o progresso da busca 
    print(f"[TRACE] Página: {pagina} - Tentativa: {tentativas + 1}/{max_tentativas}") # Log para acompanhar o número da página e tentativas

    try:
        response = requests.get( # Faz a requisição GET para a API
            API_URL,
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
    
        # Ajuste caso venha objetos
        if isinstance(data, dict):
            api_data = data.get(endpoint_cfg["responseKey"] or "data", [])
        else:
            api_data = data
                    
        # Verifica se a resposta co
        if not api_data:
            print(f"[AVISO] Nenhum dado retornado. Finalizando a busca.")
            break
        
        all_data.extend(api_data) # Adiciona os dados da página atual à lista total de dados
        tentativas = 0 # Reseta o contador de tentativas após uma resposta bem-sucedida
        print(f"[REGISTRO] Total de dados coletados até o momento: {len(all_data)}") # Log para acompanhar o número total de dados coletados
        
        # Paginação: Incrementa o parâmetro "skip" para buscar a próxima página de resultados
        if len(api_data) < params["take"]:
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

#Resultado final
print(f"[REGISTRO] Total de dados coletados: {len(all_data)}") # Log para mostrar o número total de dados coletados após o loop de busca

if not all_data:
    print("[AVISO] Nenhum dado coletado. Verifique a API e as credenciais.")
    raise SystemExit(1)
    
# Normalização dos dados e criação do DataFrame
df_sales = pd.json_normalize(all_data) # Normaliza os dados de  para criar um DataFrame
print(f"[INFO] DataFrame {arquivo} criado com sucesso.") # Log para indicar que o DataFrame foi criado com sucesso
    
# Criando um backup do dado bruto antes de qualquer transformação para garantir que o dado original esteja preservado para futuras análises ou auditorias
df_raw = df_sales.copy()  # Backup do dado bruto antes de qualquer transformação  
df_raw.to_csv(arquivo_raw, index=False, sep=";", encoding="utf-8")
print(f"[BACKUP] Backup raw salvo em '{arquivo_raw}'.")

# Limpar e renomear as colunas do DataFrame para um formato mais limpo e consistente
df_sales.columns = [col.replace(" ", "_").lower() for col in df_sales.columns] # Renomeia as colunas para um formato mais limpo (sem espaços e em minúsculas)

# Remover colunas desnecessárias (ajuste a lista de colunas a serem removidas com base na análise dos dados)
colunas_drop = ["coluna1", "coluna2", "coluna3"]  # definir após análise
df_sales.drop(columns=colunas_drop, inplace=True, errors="ignore")
    
# Verificação de duplicatas por ID (se a coluna "idsale" existir) para evitar registros duplicados em cargas incrementais
id_col = endpoint_cfg["idField"].lower()
if id_col not in df_sales.columns:
    print(f"[AVISO] Coluna '{id_col}' não encontrada. Deduplicação por ID ignorada.")
else:
    df_sales.drop_duplicates(subset=[id_col], inplace=True)
    print(f"[DROP] Registros duplicados por '{id_col}' removidos.")
    
    if os.path.exists(arquivo):
        df_old_ids = pd.read_csv(arquivo, sep=";", usecols=[id_col])
        qtd_antes = len(df_sales)
        df_sales = df_sales[~df_sales[id_col].isin(df_old_ids[id_col])]
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

print(f"[EXPORT] Dados do Endpoint exportados para {arquivo} com sucesso.") # Log para indicar que os dados foram exportados com sucesso

# Salva o checkpoint apenas se a execução foi concluída com sucesso
save_checkpoint(date_end)
