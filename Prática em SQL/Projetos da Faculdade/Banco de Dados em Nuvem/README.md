☁️ Prática de Banco de Dados em Nuvem – Modelagem de Relacionamentos

https://img.shields.io/badge/MySQL-8.0-blue
https://img.shields.io/badge/Workbench-Ferramenta-orange
https://img.shields.io/badge/Cloud-AWS%2520%257C%2520GCP%2520%257C%2520Azure-lightgrey
https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen

Este repositório contém o script SQL desenvolvido durante a disciplina Banco de Dados em Nuvem da faculdade. O objetivo é criar um banco de dados relacional localmente (MySQL Workbench) e descrever os passos para conectá‑lo a um provedor em nuvem.

📖 Sobre o Projeto
A atividade prática consistiu em:

1. Criar um banco de dados chamado aula utilizando o MySQL Workbench.
2. Implementar três tipos de relacionamentos:
  - 1:1 – Cliente e Endereço
  - 1:N – Empresa e Funcionário
  - N:N – Curso e Estudante (com tabela associativa)
3. Descrever como conectar esse banco a um provedor em nuvem (AWS, Google Cloud, Azure, etc.), incluindo características e custos.

O resultado é um script SQL completo e um roteiro para publicação em nuvem, ideal para quem está iniciando no mundo de bancos de dados relacionais e deseja entender tanto a modelagem quanto a infraestrutura em cloud.

🛠️ Tecnologias Utilizadas
  - MySQL 8.0 – Sistema de gerenciamento de banco de dados relacional
  - MySQL Workbench – Ferramenta gráfica para modelagem e administração
  - SQL – Linguagem de consulta estruturada (DDL)
  - Cloud Provider – AWS RDS, Google Cloud SQL ou Azure Database (descritivo)

📁 Estrutura do Script
-- 1) Criar o banco de dados "aula"
CREATE DATABASE aula;
USE aula;

-- 2) Relacionamento 1 para 1: Tabelas cliente e endereco
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

-- 3) Relacionamento 1 para muitos: Tabelas empresa e funcionario
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

-- 4) Relacionamento muitos para muitos: Tabelas curso, estudante e curso_estudante
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


## 🧠 Explicação dos Relacionamentos

| Tipo | Entidades | Como foi implementado |
|------|-----------|------------------------|
| 1:1  | cliente ↔ endereco | A coluna `cliente_id` em `endereco` possui a restrição `UNIQUE`, garantindo que um cliente só pode ter um endereço e vice-versa. |
| 1:N  | empresa ↔ funcionario | A tabela `funcionario` contém a chave estrangeira `empresa_id`, permitindo que vários funcionários pertençam à mesma empresa. |
| N:N  | curso ↔ estudante | Uma tabela associativa `curso_estudante` armazena pares (`curso_id`, `estudante_id`). A chave primária composta impede matrículas duplicadas. |

🚀 Como Executar Localmente
Pré‑requisitos
  - MySQL Server instalado (ou MariaDB)
  - MySQL Workbench (opcional, mas recomendado)

Passo a passo
1. Acesse o MySQL via terminal ou Workbench.
2. Execute o script completo ou copie e cole no editor SQL.
3. Verifique as tabelas criadas:
  USE aula;
  SHOW TABLES;
4. Insira dados de exemplo (opcional, veja sugestões no script).

---

☁️ Conectando o Banco a um Provedor em Nuvem
Abaixo está uma descrição genérica de como publicar o banco de dados em um ambiente cloud. Os procedimentos são semelhantes para os principais provedores.

1. Escolha um Provedor

| Provedor        | Serviço               | Características                                               | Preço aproximado (menor plano)        |
|-----------------|----------------------|---------------------------------------------------------------|--------------------------------------|
| AWS             | RDS (MySQL)          | Gerenciado, escalável, backup automático, suporte a Multi‑AZ  | ~ USD 15/mês (db.t3.micro)           |
| Google Cloud    | Cloud SQL (MySQL)    | Totalmente gerenciado, integração com VPC, réplicas de leitura | ~ USD 10/mês (db‑f1‑micro)          |
| Microsoft Azure | Database for MySQL    | Alta disponibilidade, segurança integrada, escalabilidade flexível | ~ USD 15/mês (Basic tier)         |

2. Passos Comuns
  1. Criar uma instância de banco de dados no console do provedor.
    - Escolha MySQL como engine.
    - Defina nome da instância, usuário administrador e senha.
    - Selecione a região mais próxima de você.
    - Configure o armazenamento e a classe da máquina (comece com a menor para testes).

  2. Liberar acesso:
    - No grupo de segurança (firewall), adicione uma regra permitindo conexões do seu IP atual (ou de toda a sua aplicação).
  3. Conectar via MySQL Workbench:
    - Obtenha o endpoint público da instância.
    - No Workbench, crie uma nova conexão com:
    - Hostname: endpoint fornecido
    - Port: 3306 (padrão)
    - Username: usuário administrador
    - Password: senha definida
  4. Migrar o banco local para a nuvem:
    - Utilize o recurso Data Export/Import do Workbench ou ferramentas como mysqldump.

3. Considerações Finais
  - Custos: Lembre‑se de parar/remover a instância quando não estiver em uso para evitar cobranças desnecessárias.
  - Segurança: Nunca exponha a porta 3306 para toda a internet; restrinja aos IPs necessários.
  - Backup: Os serviços gerenciados já oferecem backup automático; familiarize‑se com a política de retenção.


📝 Conclusão
Esta atividade prática permitiu consolidar os conceitos de modelagem relacional (1:1, 1:N, N:N) utilizando a linguagem SQL e a ferramenta MySQL Workbench. Além disso, a etapa de descrição da conexão com a nuvem introduziu noções importantes sobre infraestrutura como serviço (IaaS/PaaS), custos e segurança – habilidades essenciais para um profissional de dados que precisa publicar e gerenciar bancos em produção.
O script desenvolvido pode ser reutilizado como base para projetos mais complexos, e as instruções de nuvem servem como guia para uma eventual migração.

🔮 Possíveis Melhorias
  - Adicionar AUTO_INCREMENT nas chaves primárias.
  - Incluir constraints de NOT NULL e CHECK (ex.: email válido).
  - Criar índices para melhorar a performance de consultas comuns.
  - Gerar um diagrama entidade‑relacionamento (DER) visual.
  - Automatizar a criação da instância em nuvem via Terraform ou scripts.


📝 Licença <br>
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

✉️ Contato <br>
Weslley B. de Andrade – [Weslley B. de Andrade](www.linkedin.com/in/weslley-bitencourt) – [email](weslleybitencourt03@gmail.com)
Link do projeto: [biblioteca_python_v2](https://github.com/OBenzeno/Portfolio/tree/main/biblioteca_python_v2)

⭐ Se este conteúdo foi útil, deixe uma estrela no repositório!

🧩 Parte de uma série
Confira também outros projetos da faculdade:
- [Sistema de Gerenciamento de Biblioteca](https://github.com/OBenzeno/Portfolio/tree/main/biblioteca_python_v2)
- Mais projetos em breve...
