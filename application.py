import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = sqlite3.connect("budget.db", check_same_thread=False)
cur = db.cursor()
cur.row_factory = sqlite3.Row


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show/Add purchases"""
    user_id = session["user_id"]
    currentYear = date.today().strftime("%Y")
    yearsList = cur.execute(("SELECT DISTINCT strftime('%Y', data) AS year FROM compras WHERE NOT year = ? "), (currentYear,)).fetchall()
    purchases = cur.execute(
        "SELECT compras.id, SUM((compra_produto.quant * compra_produto.preco_unit)) AS total, compras.categoria_id, categoria.descricao, compras.data FROM compras " \
            "INNER JOIN categoria ON compras.categoria_id=categoria.id LEFT JOIN compra_produto ON compras.id = compra_produto.compras_id WHERE user_id = ? " \
                "GROUP BY compras.id ORDER BY compras.data DESC", (user_id,)
        ).fetchall()
    purchasesbycat = cur.execute(
        "SELECT categoria.descricao, SUM((compra_produto.quant * compra_produto.preco_unit)) AS total FROM compras " \
            "INNER JOIN categoria ON compras.categoria_id=categoria.id LEFT JOIN compra_produto ON compras.id = compra_produto.compras_id "\
            "WHERE user_id = ? AND strftime('%Y', compras.data) = ?" \
            "GROUP BY compras.categoria_id ORDER BY total DESC", (user_id, currentYear)
    ).fetchall()
    spendbymonth = cur.execute(
        "SELECT SUM((compra_produto.quant * compra_produto.preco_unit)) AS total, strftime('%m', compras.data) AS month FROM compras " \
            "LEFT JOIN compra_produto ON compras.id = compra_produto.compras_id WHERE user_id = ? AND strftime('%Y', compras.data) = ?" \
                "GROUP BY strftime('%m', compras.data) ORDER BY compras.data", (user_id, currentYear)
        ).fetchall()

    pbc = [dict(item) for item in purchasesbycat]

    category = cur.execute("SELECT id, descricao FROM categoria WHERE parent_id IS NULL").fetchall()
    
    if request.method == "POST":
        button = request.form.get("postbutton")
        purchase_id = request.form.get("id")

        if button == "remove":
            cur.execute("DELETE FROM compras WHERE id = ?", (purchase_id,))
            cur.execute("DELETE FROM compra_produto WHERE compras_id = ?", (purchase_id,))
            db.commit()
            
            flash("Removed")
        else:
            category_id = request.form.get("category")
            data = request.form.get("date")
            
            if data == '':
                data = date.today()

            if purchase_id == '':
                cur.execute("INSERT INTO compras (user_id, categoria_id, data) VALUES ( ?, ?, ?)", (user_id, category_id, data))
            else:
                cur.execute("INSERT INTO compras (id, user_id, categoria_id, data) VALUES (?, ?, ?, ?)", (purchase_id, user_id, category_id, data))
            
            db.commit()

            flash("Added")

        return redirect("/")

    else:
        return render_template("index.html", purchases=purchases, category=category, purchasesbycat=pbc, spendbymonth=spendbymonth, yearslist=yearsList, currentYear=currentYear)


@app.route("/changeyear")
@login_required
def changeyear():

    query = request.args.get('query')
    user_id = session["user_id"]

    spendbymonth = cur.execute(
    "SELECT SUM((compra_produto.quant * compra_produto.preco_unit)) AS total, strftime('%m', compras.data) AS month FROM compras " \
        "LEFT JOIN compra_produto ON compras.id = compra_produto.compras_id WHERE user_id = ? AND strftime('%Y', compras.data) = ?" \
            "GROUP BY strftime('%m', compras.data) ORDER BY compras.data", (user_id, query)
    ).fetchall()

    purchasesbycat = cur.execute(
    "SELECT categoria.descricao, SUM((compra_produto.quant * compra_produto.preco_unit)) AS total FROM compras " \
        "INNER JOIN categoria ON compras.categoria_id=categoria.id LEFT JOIN compra_produto ON compras.id = compra_produto.compras_id "\
            "WHERE user_id = ? AND strftime('%Y', compras.data) = ?" \
            "GROUP BY compras.categoria_id ORDER BY total DESC", (user_id, query)
    ).fetchall()

    spendMonth = [dict(item) for item in spendbymonth]
    spendCat = [dict(item) for item in purchasesbycat]
    print(spendMonth)
    print(spendCat)

    return jsonify(spendMonth=spendMonth, spendCat=spendCat)


# source: https://tutorial101.blogspot.com/2021/02/python-flask-jquery-ajax-live-data.html
@app.route("/items", methods=["GET", "POST"])
@login_required
def items():
    """add product to database"""
    addItems = request.args.get("idadditems")
    shopping_list = cur.execute("SELECT id FROM compras ORDER BY data DESC").fetchall()
    categories = cur.execute("SELECT * FROM categoria WHERE parent_id IS NULL").fetchall()
    subcategories = cur.execute("SELECT * FROM categoria WHERE parent_id IS NOT NULL").fetchall()
    buttonValue = request.form.get('postbutton')

    itemList = cur.execute(
        "SELECT produto.id, produto.produto_nome, c.descricao AS category, categoria.descricao AS subcategory FROM produto " \
            "INNER JOIN produto_categoria ON produto.id=produto_categoria.id_produto " \
                "INNER JOIN categoria ON produto_categoria.id_categoria=categoria.id "\
                    "INNER JOIN (SELECT id, descricao FROM categoria WHERE parent_id IS NULL) c ON categoria.parent_id=c.id " \
                        "ORDER BY category"
    )

    if request.method == "POST":
        if buttonValue == "edit":
            print("edit")
            newId = request.form.get('newId')
            oldId = request.form.get('oldId')
            newName = request.form.get('newName').lower()
            newSub = request.form.get('newSub')

            if newName != '':
                cur.execute("UPDATE produto SET produto_nome = ? WHERE id = ?", (newName, oldId))

            if newId != '':
                cur.execute("UPDATE produto SET id = ? WHERE id = ?", (newId, oldId))
                cur.execute("UPDATE produto_categoria SET id_produto = ? WHERE id_produto = ?", (newId, oldId))
                cur.execute("UPDATE compra_produto SET produto_id = ? WHERE produto_id = ?", (newId, oldId))

            if newSub is not None:
                cur.execute("UPDATE produto_categoria SET id_categoria = ? WHERE id_produto = ?", (newSub, newId))

            db.commit()

            flash("Item Edited")

        elif buttonValue == "remove":
            itemId = request.form.get('id')
            cur.execute("DELETE FROM produto WHERE id = ?", (itemId,))
            cur.execute("DELETE FROM produto_categoria WHERE id_produto = ?", (itemId,))
            cur.execute("DELETE FROM compra_produto WHERE produto_id = ?", (itemId,))
            
            db.commit()
            
            flash("Item Removed")

        else:
            purchases_id = request.form.get("purchases")
            product_name = request.form.get("product_name").lower()
            subcategory = request.form.get("subcategory").lower()
            quantity = request.form.get("quantity")
            place = request.form.get("place").lower()
            unit_price = request.form.get("unit_price")
            catId = cur.execute("SELECT categoria_id FROM compras WHERE id = ?", (purchases_id,)).fetchone()[0]
            productId = cur.execute("SELECT id FROM produto WHERE produto_nome = ?", (product_name,)).fetchone()
            subcatId = cur.execute("SELECT id FROM categoria WHERE descricao = ? AND parent_id IS NOT NULL", (subcategory,)).fetchone()
            placeId = cur.execute("SELECT id FROM fornecedor WHERE fornecedor_nome = ?", (place,)).fetchone()

            if subcatId is None:
                maxId = cur.execute("SELECT MAX (id) FROM categoria WHERE parent_id = ? GROUP BY parent_id", (catId,)).fetchone()
                if maxId:
                    subcatId = maxId[0] + 1
                    cur.execute(
                        "INSERT INTO categoria (id, descricao, parent_id) VALUES (?, ?, ?)", (subcatId, subcategory, catId)
                        )
                else:
                    subcatId = catId * 100
                    cur.execute(
                        "INSERT INTO categoria (id, descricao, parent_id) VALUES (?, ?, ?)", (subcatId, subcategory, catId)
                        )
            else:
                subcatId = subcatId[0]

            if productId is None:
                cur.execute(
                    "INSERT INTO produto (produto_nome) VALUES (?)", (product_name,)
                    )
                productId = cur.execute("SELECT id FROM produto WHERE produto_nome = ?", (product_name,)).fetchone()[0]
                cur.execute(
                    "INSERT INTO produto_categoria (id_produto, id_categoria) VALUES (?, ?)", (productId, subcatId)
                    )
            else:
                productId = productId[0]
            
            if placeId is None:
                cur.execute(
                    "INSERT INTO fornecedor (fornecedor_nome) VALUES (?)", (place,)
                    )
                placeId = cur.execute("SELECT id FROM fornecedor WHERE fornecedor_nome = ?", (place,)).fetchone()[0]
            else:
                placeId = placeId[0]

            cur.execute(
                "INSERT INTO compra_produto (produto_id, quant, fornecedor_id, compras_id, preco_unit) VALUES (?, ?, ?, ?, ?)", (
                productId, quantity, placeId, purchases_id, unit_price)
                )
            
            flash("Item Added")

        db.commit()

        return redirect("/items")

    else:

        return render_template("items.html", shopping_list=shopping_list, addItems=addItems, itemList=itemList, subcategories=subcategories, categories=categories)


@app.route("/fetchsubcat")
@login_required
def fetchsubcat():
    query_sub = request.args.get('query_sub')
    query = request.args.get('query')

    if query_sub:
        parent_id = cur.execute("SELECT categoria_id FROM compras WHERE id = ?", (query_sub,)).fetchone()[0]
    else:
        parent_id = query

    data_sub = cur.execute("SELECT id, descricao FROM categoria WHERE parent_id = ?", (parent_id,)).fetchall()
    sublist = [dict(row) for row in data_sub]

    return jsonify(sublist=sublist, parentid=parent_id)


@app.route("/fetchprod")
@login_required
def fetchprod():
    data_prod = cur.execute("SELECT * FROM produto").fetchall()
    data_sup = cur.execute("SELECT * FROM fornecedor").fetchall()

    productlist = [dict(row) for row in data_prod]
    placelist = [dict(row) for row in data_sup]

    return jsonify(productlist=productlist, placelist=placelist)


@app.route("/fetchpur")
@login_required
def fetchpur():
    query = request.args.get("query")

    data = cur.execute(
        "SELECT produto.produto_nome, SUM(compra_produto.quant) AS quant, categoria.descricao, compra_produto.preco_unit, fornecedor.fornecedor_nome " \
            "FROM compra_produto INNER JOIN produto ON compra_produto.produto_id = produto.id " \
                "INNER JOIN fornecedor ON compra_produto.fornecedor_id = fornecedor.id INNER JOIN produto_categoria ON compra_produto.produto_id = produto_categoria.id_produto " \
                    "INNER JOIN categoria ON produto_categoria.id_categoria = categoria.id " \
                    "WHERE compras_id = ? GROUP BY produto.id", (query,)
        ).fetchall()
    
    purlist = [dict(row) for row in data]
    for row in purlist:
        row['total'] = row['quant'] * row['preco_unit']

    return jsonify(purlist=purlist)


@app.route("/category", methods=["GET", "POST"])
@login_required
def category():
    """Categories section"""
    categories = cur.execute("SELECT * FROM categoria WHERE parent_id IS NULL").fetchall()
    subcategories = cur.execute("SELECT * FROM categoria WHERE parent_id IS NOT NULL").fetchall()

    if request.method == "POST":
        button = request.form.get("postbutton")

        if button == "remove":
            catId = request.form.get("id")
            cur.execute("DELETE FROM categoria WHERE id = ?", (catId,))
            cur.execute("DELETE FROM categoria WHERE parent_id = ?", (catId,))

            flash("Category Removed")

        elif button == "edit":
            oldId = request.form.get("oldId")
            newId = request.form.get("newId")
            newDescription = request.form.get("newDescription").lower()
            newParent = request.form.get("newParent")

            if newDescription != '':
                cur.execute("UPDATE categoria SET descricao = ? WHERE id = ?", (newDescription, oldId))

            if newParent is not None:
                cur.execute("UPDATE categoria SET parent_id = ? WHERE id = ?", (newParent, oldId))
            
            if newId != '':
                cur.execute("UPDATE categoria SET id = ? WHERE id = ?", (newId, oldId))
                cur.execute("UPDATE produto_categoria SET id_categoria = ? WHERE id_categoria = ?", (newId, oldId))
                
            flash("Category Edited")
        else:
            catId = request.form.get("categoryId")
            catDesc = request.form.get("catDesc")
            catParent = request.form.get("catParent")

            cur.execute("INSERT INTO categoria (id, descricao, parent_id) VALUES (?, ?, ?)", (catId, catDesc, catParent))

            flash("Category Added")

        db.commit()

        return redirect("/category")

    return render_template("category.html", category_list=categories, subcategories=subcategories)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Modified. source = flask tutorial
        error = None
        # Ensure username was submitted
        username = request.form.get('username')
        password = request.form.get('password')

        # Query database for username

        user = cur.execute("SELECT * FROM user WHERE username = (?)", (username,)).fetchone()

        # Ensure username exists and password is correct
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # Remember which user has logged in
        if error is None:
            session["user_id"] = user["id"]
        
        flash(error)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        error = None

        if request.form.get("password") != request.form.get("confirmation"):
            error = "Passwords must be the same"

        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = cur.execute("SELECT * FROM user WHERE username = (?)", (username,)).fetchone()

        # Ensure username do not exist yet
        if rows != None:
            error = "username already exists"

        # Query database for username
        cur.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password),))
        db.commit()

        flash(error)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
