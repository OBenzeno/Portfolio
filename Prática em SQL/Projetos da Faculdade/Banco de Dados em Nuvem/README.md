# ☁️ Prática de Banco de Dados em Nuvem – Modelagem de Relacionamentos

![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)
![Workbench](https://img.shields.io/badge/Workbench-Ferramenta-orange)
![Cloud](https://img.shields.io/badge/Cloud-AWS%20%7C%20GCP%20%7C%20Azure-lightgrey)
![Status](https://img.shields.io/badge/status-concluído-brightgreen)

Este repositório contém o script SQL desenvolvido durante a disciplina Banco de Dados em Nuvem da faculdade.  
O objetivo é criar um banco de dados relacional localmente (MySQL Workbench) e descrever os passos para conectá‑lo a um provedor em nuvem.

---

## 📖 Sobre o Projeto

A atividade prática consistiu em:

1. Criar um banco de dados chamado `aula` utilizando o MySQL Workbench.
2. Implementar três tipos de relacionamentos:
   - **1:1** – Cliente e Endereço
   - **1:N** – Empresa e Funcionário
   - **N:N** – Curso e Estudante (com tabela associativa)
3. Descrever como conectar esse banco a um provedor em nuvem (AWS, Google Cloud, Azure, etc.), incluindo características e custos.

O resultado é um script SQL completo e um roteiro para publicação em nuvem, ideal para iniciantes em bancos de dados relacionais.

---

## 🛠️ Tecnologias Utilizadas

- **MySQL 8.0** – Sistema de gerenciamento de banco de dados relacional  
- **MySQL Workbench** – Ferramenta gráfica para modelagem e administração  
- **SQL** – Linguagem de consulta estruturada (DDL)  
- **Cloud Provider** – AWS RDS, Google Cloud SQL ou Azure Database (descritivo)

---

## 📁 Estrutura do Script

### 1) Criar o banco de dados "aula"

```sql
CREATE DATABASE aula;
USE aula;
```

### 2) Relacionamento 1:1 – Tabelas cliente e endereco

```sql
CREATE TABLE cliente (
    cliente_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50)
);

CREATE TABLE endereco (
    endereco_id INT PRIMARY KEY,
    cliente_id INT UNIQUE, -- garante 1:1
    rua VARCHAR(100),
    cidade VARCHAR(50),
    estado VARCHAR(50),
    pais VARCHAR(50),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
);
```

### 3) Relacionamento 1:N – Tabelas empresa e funcionario

```sql
CREATE TABLE empresa (
    empresa_id INT PRIMARY KEY,
    nome VARCHAR(50),
    endereco VARCHAR(100)
);

CREATE TABLE funcionario (
    funcionario_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50),
    empresa_id INT,
    FOREIGN KEY (empresa_id) REFERENCES empresa(empresa_id)
);
```

## 4) Relacionamento N:N – Tabelas curso, estudante e curso_estudante

```sql
CREATE TABLE curso (
    curso_id INT PRIMARY KEY,
    nome VARCHAR(50),
    descricao VARCHAR(100)
);

CREATE TABLE estudante (
    estudante_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50)
);

CREATE TABLE curso_estudante (
    curso_id INT,
    estudante_id INT,
    PRIMARY KEY (curso_id, estudante_id),
    FOREIGN KEY (curso_id) REFERENCES curso(curso_id),
    FOREIGN KEY (estudante_id) REFERENCES estudante(estudante_id)
);
```

## 🧠 Explicação dos Relacionamentos

| Tipo | Entidades | Como foi implementado |
|------|-----------|----------------------|
| 1:1  | cliente ↔ endereco | A coluna `cliente_id` em `endereco` possui a restrição `UNIQUE`, garantindo que um cliente só pode ter um endereço. |
| 1:N  | empresa ↔ funcionario | A tabela `funcionario` contém a chave estrangeira `empresa_id`, permitindo que vários funcionários pertençam à mesma empresa. |
| N:N  | curso ↔ estudante | A tabela associativa `curso_estudante` armazena pares (`curso_id`, `estudante_id`). A chave primária composta impede matrículas duplicadas. |

---

## 🚀 Como Executar Localmente

### Pré‑requisitos
- MySQL Server instalado (ou MariaDB)  
- MySQL Workbench (opcional, mas recomendado)  

### Passo a passo
1. Acesse o MySQL via terminal ou Workbench.  
2. Execute o script completo ou copie e cole no editor SQL.  
3. Verifique as tabelas criadas:
```sql
USE aula;
SHOW TABLES;
```
4. Insira dados de exemplo (opcional, veja sugestões no script).

## ☁️ Conectando o Banco a um Provedor em Nuvem

### 1. Escolha um Provedor

| Provedor        | Serviço               | Características                                               | Preço aproximado (menor plano)        |
|-----------------|----------------------|---------------------------------------------------------------|--------------------------------------|
| AWS             | RDS (MySQL)          | Gerenciado, escalável, backup automático, suporte a Multi‑AZ  | ~ USD 15/mês (db.t3.micro)           |
| Google Cloud    | Cloud SQL (MySQL)    | Totalmente gerenciado, integração com VPC, réplicas de leitura | ~ USD 10/mês (db‑f1‑micro)          |
| Microsoft Azure | Database for MySQL    | Alta disponibilidade, segurança integrada, escalabilidade flexível | ~ USD 15/mês (Basic tier)         |

---

### 2. Passos Comuns

1. **Criar uma instância de banco de dados no console do provedor:**  
   - Escolha MySQL como engine  
   - Defina nome da instância, usuário administrador e senha  
   - Selecione a região mais próxima  
   - Configure armazenamento e classe da máquina (comece com a menor para testes)  

2. **Liberar acesso:**  
   - No grupo de segurança (firewall), adicione uma regra permitindo conexões do seu IP ou aplicação  

3. **Conectar via MySQL Workbench:**  
   - Obtenha o endpoint público da instância  
   - Crie uma nova conexão com:  
     - **Hostname:** endpoint fornecido  
     - **Port:** 3306 (padrão)  
     - **Username:** usuário administrador  
     - **Password:** senha definida  

4. **Migrar o banco local para a nuvem:**  
   - Utilize Data Export/Import do Workbench ou ferramentas como `mysqldump`  

---

### 3. Considerações Finais

- **Custos:** Pare/remova a instância quando não estiver em uso  
- **Segurança:** Não exponha a porta 3306 para toda a internet; restrinja aos IPs necessários  
- **Backup:** Serviços gerenciados oferecem backup automático; confira a política de retenção  

---

## 📝 Conclusão

Esta atividade prática consolidou conceitos de modelagem relacional (1:1, 1:N, N:N) utilizando SQL e MySQL Workbench.  
A etapa de conexão com a nuvem introduziu noções de infraestrutura como serviço (IaaS/PaaS), custos e segurança.  
O script pode servir como base para projetos mais complexos, e as instruções de nuvem como guia de migração.  

---

## 🔮 Possíveis Melhorias

- Adicionar `AUTO_INCREMENT` nas chaves primárias  
- Incluir `NOT NULL` e `CHECK` (ex.: email válido)  
- Criar índices para melhorar performance  
- Gerar um diagrama entidade‑relacionamento (DER) visual  
- Automatizar a criação da instância em nuvem via Terraform ou scripts  

📝 Licença <br>
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

✉️ Contato <br>
Weslley B. de Andrade – [Linkedin](www.linkedin.com/in/weslley-bitencourt)
[email](weslleybitencourt03@gmail.com)
Link do projeto:[Banco de Dados em Nuvem](https://github.com/OBenzeno/Portfolio/blob/main/Pr%C3%A1tica%20em%20SQL/Projetos%20da%20Faculdade/Banco%20de%20Dados%20em%20Nuvem/pratica_cloud_db_aula.sql)

⭐ Se este conteúdo foi útil, deixe uma estrela no repositório!

🧩 Parte de uma série
Confira também outros projetos da faculdade:
- [Sistema de Gerenciamento de Biblioteca](https://github.com/OBenzeno/Portfolio/tree/main/biblioteca_python_v2)
- [Data Warehouse do Jockey Club](https://github.com/OBenzeno/Portfolio/tree/main/Pr%C3%A1tica%20em%20SQL/Projetos%20da%20Faculdade/Arquitetura%20de%20Dados)
- [Modelagem de Dados – Sistema de Biblioteca Universitária](https://github.com/OBenzeno/Portfolio/tree/main/Pr%C3%A1tica%20em%20SQL/Projetos%20da%20Faculdade/Modelagem%20de%20Dados)
- Mais projetos em breve...
