CREATE TABLE categoria (
    id INTEGER PRIMARY KEY NOT NULL,
    descricao VARCHAR(30),
    parent_id INTEGER
);

CREATE TABLE fornecedor (
    id INTEGER PRIMARY KEY NOT NULL,
    fornecedor_nome VARCHAR(30)
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE produto (
    id INTEGER PRIMARY KEY NOT NULL,
    produto_nome VARCHAR(30)
);

CREATE TABLE produto_categoria (
    id INTEGER PRIMARY KEY NOT NULL,
    id_produto INTEGER,
    id_categoria INTEGER,
    FOREIGN KEY (id_produto) REFERENCES produto(id),
    FOREIGN KEY (id_categoria) REFERENCES categoria(id)
);

CREATE TABLE compra_produto (
    id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER,
    produto_id INTEGER,
    quant DECIMAL(15,2),
    fornecedor_id INTEGER,
    compras_id INTEGER,
    preco_unit DECIMAL (15,2),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (produto_id) REFERENCES produto(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedor(id)
    FOREIGN KEY (compras_id) REFERENCES compras(id)
);

CREATE TABLE compras (
    id INTEGER PRIMARY KEY NOT NULL,
    compra_total DECIMAL(15,2),
    categoria_id INTEGER,
    data DATE,
    FOREIGN KEY (categoria_id) REFERENCES categoria(id)
);

CREATE TABLE produto_categoria (
    id_produto INTEGER,
    id_categoria INTEGER,
    PRIMARY KEY(id_produto, id_categoria)
    FOREIGN KEY (id_produto) REFERENCES produto(id),
    FOREIGN KEY (id_categoria) REFERENCES categoria(id)
);

