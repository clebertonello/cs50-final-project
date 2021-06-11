import sqlite3
from datetime import date
import json

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
    (1, 'BIGLAR'),
    (2, 'COMPER'),
    (3, 'FORT'),
    (4, 'ATACADÃO'),
    (5, 'STUDIO STEEL WORKOUT')
]

produto_categoria = [
    (7898964981113,100),
    (789864981021,100),
    (7898908804287,100),
    (7896002360326,106)
    ]

#cur.executemany('INSERT INTO categoria (descricao, parent_id) VALUES (?, ?)', categorias)

#cur.executemany('INSERT INTO categoria (id, descricao, parent_id) VALUES (?, ?, ?)', subcategorias)
""" 
cur.executemany('INSERT INTO fornecedor (id, fornecedor_nome) VALUES (?, ?)', fornecedores)

db.commit() """


cur.executemany('INSERT INTO produto_categoria (id_produto, id_categoria) VALUES (?, ?)', produto_categoria)

db.commit()

#category_list = cur.execute("SELECT descricao FROM categoria WHERE parent_id IS NULL").fetchall()
#print(category_list[0]['descricao'])

""" query = 'Mercado'
parent_id = cur.execute("SELECT id FROM categoria WHERE descricao = ?", (query,)).fetchone()[0]
print(parent_id) """

""" parent_id = 1
sublist = []
data = cur.execute("SELECT descricao FROM categoria WHERE parent_id = ?", (parent_id,)).fetchall()

for i in data:
    sublist.append(list(i)) """

""" 
cur.execute("INSERT INTO compras (id, compra_total, categoria_id, data) VALUES (?, ?, ?, ?)", (20210610001, 204, 6, date.today()))
db.commit() """

""" purchases = cur.execute(
    "SELECT compras.id, compras.compra_total, categoria.descricao, compras.data FROM compras INNER JOIN categoria ON compras.categoria_id=categoria.id"
    ).fetchone() """
"""
var = cur.execute("SELECT MAX (id) FROM categoria WHERE parent_id = 6 GROUP BY parent_id").fetchone()
print(var[0])

result = [dict(row) for row in shopping_list]
json.dumps(result)
print(result) """




