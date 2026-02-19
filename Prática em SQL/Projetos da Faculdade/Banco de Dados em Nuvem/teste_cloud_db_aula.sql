CREATE DATABASE aula;
USE aula;

CREATE TABLE cliente (
    cliente_id INT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50)
);

CREATE TABLE endereco (
    endereco_id INT PRIMARY KEY,
    cliente_id INT UNIQUE,
    rua VARCHAR(100),
    cidade VARCHAR(50),
    estado VARCHAR(50),
    pais VARCHAR(50),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
);

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
