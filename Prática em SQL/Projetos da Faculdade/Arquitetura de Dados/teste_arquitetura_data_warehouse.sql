-- Criação do banco de dados
CREATE DATABASE jantar_eventos;

-- Seleção do banco de dados
USE jantar_eventos;

-- Tabela para armazenar informações dos membros
CREATE TABLE members (
    member_num INT PRIMARY KEY,
    member_name VARCHAR(50),
    member_address VARCHAR(100),
    dinners_dinner_num INT,
    FOREIGN KEY (dinners_dinner_num) REFERENCES dinners(dinner_num)
);

-- Tabela para armazenar informações dos locais (venues)
CREATE TABLE venues (
    venue_code INT PRIMARY KEY,
    venue_description VARCHAR(50),
    dinners_dinner_num INT,
    FOREIGN KEY (dinners_dinner_num) REFERENCES dinners(dinner_num)
);

-- Tabela para armazenar os jantares (dinners)
CREATE TABLE dinners (
    dinner_num INT PRIMARY KEY,
    dinner_date DATE,
    member_num INT,
    dinner_items_dinner_num INT,
    dinner_items_food_code VARCHAR(45),
    FOREIGN KEY (member_num) REFERENCES members(member_num),
    FOREIGN KEY (dinner_items_dinner_num) REFERENCES dinner_items(dinner_num),
    FOREIGN KEY (dinner_items_food_code) REFERENCES food_items(food_code)
);

-- Tabela para armazenar os itens de jantar (dinner_items)
CREATE TABLE dinner_items (
    dinner_num INT,
    food_code VARCHAR(45),
    PRIMARY KEY (dinner_num, food_code),
    FOREIGN KEY (dinner_num) REFERENCES dinners(dinner_num),
    FOREIGN KEY (food_code) REFERENCES food_items(food_code)
);

-- Tabela para armazenar os itens de comida (food_items)
CREATE TABLE food_items (
    food_code VARCHAR(45) PRIMARY KEY,
    food_description VARCHAR(50),
    dinner_items_dinner_num INT,
    dinner_items_food_code VARCHAR(45),
    FOREIGN KEY (dinner_items_dinner_num) REFERENCES dinner_items(dinner_num),
    FOREIGN KEY (dinner_items_food_code) REFERENCES dinner_items(food_code)
);

