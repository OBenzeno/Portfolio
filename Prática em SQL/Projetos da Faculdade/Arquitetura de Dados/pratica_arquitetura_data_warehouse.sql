-- Tabela para armazenar os jantares
CREATE TABLE dinners (
    dinner_num INT PRIMARY KEY,
    dinner_date DATE
);

-- Tabela para armazenar os membros
CREATE TABLE members (
    member_num INT PRIMARY KEY,
    member_name VARCHAR(50),
    member_address VARCHAR(100)
);

-- Tabela para associar membros a jantares (relacionamento muitos para muitos)
CREATE TABLE member_dinners (
    member_num INT,
    dinner_num INT,
    PRIMARY KEY (member_num, dinner_num),
    FOREIGN KEY (member_num) REFERENCES members(member_num),
    FOREIGN KEY (dinner_num) REFERENCES dinners(dinner_num)
);

-- Tabela para armazenar os locais dos jantares
CREATE TABLE venues (
    venue_code INT PRIMARY KEY,
    venue_description VARCHAR(50)
);

-- Tabela para associar jantares aos locais
CREATE TABLE dinner_venues (
    dinner_num INT,
    venue_code INT,
    PRIMARY KEY (dinner_num, venue_code),
    FOREIGN KEY (dinner_num) REFERENCES dinners(dinner_num),
    FOREIGN KEY (venue_code) REFERENCES venues(venue_code)
);

-- Tabela para armazenar os itens de comida
CREATE TABLE food_items (
    food_code VARCHAR(45) PRIMARY KEY,
    food_description VARCHAR(50)
);

-- Tabela para armazenar os itens de jantar (muitos para muitos)
CREATE TABLE dinner_items (
    dinner_num INT,
    food_code VARCHAR(45),
    PRIMARY KEY (dinner_num, food_code),
    FOREIGN KEY (dinner_num) REFERENCES dinners(dinner_num),
    FOREIGN KEY (food_code) REFERENCES food_items(food_code)
);
