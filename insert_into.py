import sqlite3
from datetime import date
import json

db = sqlite3.connect("budget.db")
cur = db.cursor()

cur.row_factory = sqlite3.Row

#sql_file = open("script.sql")
#sql_as_string = sql_file.read()

#cur.executescript(sql_as_string)

categories = [
    'housing',
    'transportation',
    'food',
    'utilities',
    'healthcare',
    'personal',
    'education',
    'entertainment',
    'gifts/donations',
    'savings'
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

compras= [
    (20210606001, 1, 1, '2021-06-09'),
    (20210610001, 1, 6, '2021-06-10')
]

itemList = cur.execute(
    "SELECT produto.id, produto.produto_nome, c.descricao AS category, categoria.descricao AS subcategory FROM produto " \
        "INNER JOIN produto_categoria ON produto.id=produto_categoria.id_produto " \
            "INNER JOIN categoria ON produto_categoria.id_categoria=categoria.id "\
                "INNER JOIN (SELECT id, descricao FROM categoria WHERE parent_id IS NULL) c ON categoria.parent_id=c.id " \
                    "ORDER BY category"
)

    
now = [dict(row) for row in itemList]

print(now)


