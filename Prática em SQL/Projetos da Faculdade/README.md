# 📁 Práticas de SQL – Faculdade de Ciência de Dados

![SQL](https://img.shields.io/badge/SQL-MySQL-blue)
![Workbench](https://img.shields.io/badge/Workbench-Modelagem-orange)
![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)

Este repositório reúne todas as atividades práticas desenvolvidas durante as disciplinas de banco de dados da faculdade. Cada pasta corresponde a uma prática específica, contendo scripts SQL, diagramas e documentação.

---

## 📂 Estrutura de Pastas
```
📦 Projetos da Faculdade/
├── 📁 Arquitetura de Dados/
│   ├── 📁 DER/
│   │   └── diagrama_er_arquitetura_data_warehouse.png
│   ├── diagrama_er_arquitetura_data_warehouse.mwb
│   ├── 📄 pratica_arquitetura_data_warehouse.sql
│   ├── 📄 teste_arquitetura_data_warehouse.sql
│   └── 📄 README.md (detalhes da prática)
├── 📁 Banco de Dados em Nuvem/
│   ├── 📄 pratica_cloud_db_aula.sql
│   ├── 📄 teste_cloud_db_aula.sql
│   └── 📄 README.md
├── 📁 Modelagem de Dados
│   ├── diagrama_er_biblioteca.png
│   ├── 📄 diagrama_er_biblioteca.mwb
│   └── 📄 README.md
├── 📁 backup
│   ├── diagrama_er_biblioteca.bak
│   ├── diagrama_er_biblioteca.mwb.bak
│   ├── diagrama_er_dinner_service.bak
│   └── pratica_arquitetura_data_warehouse.bak
├── 📁 projetos_futuros...
└── 📄 README.md (este arquivo)
```

---

## 🗂️ Descrição das Pastas

| Pasta | Conteúdo |
|-------|----------|
| `pratica01_modelagem_biblioteca` | Diagrama Entidade-Relacionamento (DER) para sistema de biblioteca universitária. |
| `pratica02_normalizacao_restaurante` | Processo de normalização (1FN → 3FN) de uma tabela de Data Warehouse de um restaurante. |
| `pratica03_cloud_database` | Criação de banco de dados local e descrição de conexão com provedores em nuvem (AWS, GCP, Azure). |
| `pratica04_consultas_avancadas` | Scripts com consultas SQL complexas (junções, subconsultas, agregações). |
| *(outras práticas serão adicionadas conforme avanço do curso)* | ... |

---

## 🛠️ Como Utilizar

1. Navegue até a pasta de interesse.
2. Abra o arquivo `README.md` de cada prática para entender o contexto e os objetivos.
3. Execute os scripts SQL em um ambiente **MySQL** (Workbench, linha de comando, etc.) para reproduzir os exemplos.

---

## 📌 Observações

- Todos os scripts foram testados com **MySQL 8.0**.
- Os diagramas foram criados no **MySQL Workbench** (arquivos `.mwb` ou imagens `.png`).
- Sinta-se à vontade para explorar, modificar e usar como referência para seus estudos.

---

📅 **Atualizado em:** 2026
