-- 1) Criar o banco de dados "aula"
CREATE DATABASE aula;

-- Selecionar o banco de dados para uso
USE aula;

-- 2) Relacionamento 1 para 1: Tabelas cliente e endereco

-- Tabela cliente
CREATE TABLE cliente (
    cliente_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50)
);

-- Tabela endereco
CREATE TABLE endereco (
    endereco_id INT PRIMARY KEY,
    cliente_id INT UNIQUE, -- Relacionamento 1 para 1 com cliente
    rua VARCHAR(100),
    cidade VARCHAR(50),
    estado VARCHAR(50),
    pais VARCHAR(50),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
);

-- 3) Relacionamento 1 para muitos: Tabelas empresa e funcionario

-- Tabela empresa
CREATE TABLE empresa (
    empresa_id INT PRIMARY KEY,
    nome VARCHAR(50),
    endereco VARCHAR(100)
);

-- Tabela funcionario
CREATE TABLE funcionario (
    funcionario_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50),
    empresa_id INT, -- Relacionamento 1 para muitos com empresa
    FOREIGN KEY (empresa_id) REFERENCES empresa(empresa_id)
);

-- 4) Relacionamento muitos para muitos: Tabelas curso, estudante e curso_estudante

-- Tabela curso
CREATE TABLE curso (
    curso_id INT PRIMARY KEY,
    nome VARCHAR(50),
    descricao VARCHAR(100)
);

-- Tabela estudante
CREATE TABLE estudante (
    estudante_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50)
);

-- Tabela associativa curso_estudante (Relacionamento muitos para muitos)
CREATE TABLE curso_estudante (
    curso_id INT,
    estudante_id INT,
    PRIMARY KEY (curso_id, estudante_id), -- Chave primária composta
    FOREIGN KEY (curso_id) REFERENCES curso(curso_id),
    FOREIGN KEY (estudante_id) REFERENCES estudante(estudante_id)
);
