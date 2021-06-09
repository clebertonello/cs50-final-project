import sqlite3

db = sqlite3.connect("mercado.db")
cur = db.cursor()

cur.row_factory = sqlite3.Row

#sql_file = open("script.sql")
#sql_as_string = sql_file.read()

#cur.executescript(sql_as_string)

categorias = [
    ('Mercado', None),
    ('Serviço', None),
    ('Alimentação', None),
    ('Farmácia', None),
    ('Transporte', None),
    ('Fitness', None),
    ('Entrenimento', None),
    ('Outros', None),
]

subcategorias = [
    (100, 'legumes e verduas', 1),
    (101, 'proteínas', 1),
    (102, 'higiene', 1),
    (103, 'laticíneos', 1),
    (104, 'frutas', 1),
    (105, 'sobremesas', 1),
    (106, 'pães e bolos', 1),
    (107, 'temperos', 1)
]

fornecedores = [
    (1, 'BigLar', 1),
    (2, 'Comper', 1),
    (3, 'Fort', 1),
    (4, 'Atacadão', 1)
]

#cur.executemany('INSERT INTO categoria (descricao, parent_id) VALUES (?, ?)', categorias)

#cur.executemany('INSERT INTO categoria (id, descricao, parent_id) VALUES (?, ?, ?)', subcategorias)

#cur.executemany('INSERT INTO fornecedor (id, fornecedor_nome, parent_id) VALUES (?, ?, ?)', fornecedores)

#db.commit()

#category_list = cur.execute("SELECT descricao FROM categoria WHERE parent_id IS NULL").fetchall()
#print(category_list[0]['descricao'])

""" query = 'Mercado'
parent_id = cur.execute("SELECT id FROM categoria WHERE descricao = ?", (query,)).fetchone()[0]
print(parent_id) """

parent_id = 1
sublist = []
data = cur.execute("SELECT descricao FROM categoria WHERE parent_id = ?", (parent_id,)).fetchall()

for i in data:
    sublist.append(list(i))

print(sublist)



