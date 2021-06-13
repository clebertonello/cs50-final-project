import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import pandas_datareader.data as wd
from datetime import date
import json

from helpers import apology, login_required, lookup, usd

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
db = sqlite3.connect("mercado.db", check_same_thread=False)
cur = db.cursor()
cur.row_factory = sqlite3.Row


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show/Add purchases"""
    user_id = session["user_id"]
    purchases = cur.execute(
        "SELECT compras.id, SUM((compra_produto.quant * compra_produto.preco_unit)) AS total, compras.categoria_id, categoria.descricao, compras.data FROM compras " \
            "INNER JOIN categoria ON compras.categoria_id=categoria.id LEFT JOIN compra_produto ON compras.id = compra_produto.compras_id WHERE user_id = ? " \
                "GROUP BY compras.id ORDER BY compras.data DESC", (user_id,)
        ).fetchall()
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

            if purchase_id == '':
                cur.execute("INSERT INTO compras (user_id, categoria_id, data) VALUES ( ?, ?, ?)", (user_id, category_id, data))
            else:
                cur.execute("INSERT INTO compras (id, user_id, categoria_id, data) VALUES (?, ?, ?, ?)", (purchase_id, user_id, category_id, data))
            
            db.commit()

            flash("Added")

        return redirect("/")

    else:
        return render_template("index.html", purchases=purchases, category=category)


# source: https://tutorial101.blogspot.com/2021/02/python-flask-jquery-ajax-live-data.html
@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    """add product to database"""

    shopping_list = cur.execute("SELECT id FROM compras").fetchall()

    if request.method == "POST":
        purchases_id = request.form.get("purchases")
        product_id = request.form.get("id")
        product_name = request.form.get("product_name").upper()
        category_id = cur.execute("SELECT categoria_id FROM compras WHERE id = ?", (purchases_id,)).fetchone()[0]
        subcategory = request.form.get("subcategory").upper()
        subcategory_id = request.form.get("subcategoryid")
        quantity = request.form.get("quantity")
        supplier = request.form.get("supplier").upper()
        supplier_id = request.form.get("supplierid")
        unit_price = request.form.get("unit_price")

        product_check = cur.execute("SELECT id FROM produto WHERE id = ?", (product_id,)).fetchone()
        category_check = cur.execute("SELECT id FROM categoria WHERE id = ?", (subcategory_id,)).fetchone()

        if category_check is None:
            cur.execute(
                "INSERT INTO categoria (id, descricao, parent_id) VALUES (?, ?, ?)", (subcategory_id, subcategory, category_id)
                )

        if product_check is None:
            cur.execute(
                "INSERT INTO produto_categoria (id_produto, id_categoria) VALUES (?, ?)", (product_id, subcategory_id)
                )
            cur.execute(
                "INSERT INTO produto (id, produto_nome) VALUES (?, ?)", (product_id, product_name)
                )
        
        if supplier_id is None:
            cur.execute(
                "INSERT INTO fornecedor (id, produto_nome) VALUES (?, ?)", (supplier_id, supplier)
                )

        cur.execute(
            "INSERT INTO compra_produto (produto_id, quant, fornecedor_id, compras_id, preco_unit) VALUES (?, ?, ?, ?, ?)", (
            product_id, quantity, supplier_id, purchases_id, unit_price)
            )
        db.commit()

        flash("Item Added")

        return redirect("/products")

    else:

        return render_template("products.html", shopping_list=shopping_list)


@app.route("/fetchsubcat")
@login_required
def fetchsubcat():
    query_sub = request.args.get('query_sub')
    parent_id = cur.execute("SELECT categoria_id FROM compras WHERE id = ?", (query_sub,)).fetchone()[0]
    max_value = cur.execute("SELECT MAX (id) FROM categoria WHERE parent_id = ? GROUP BY parent_id", (parent_id,)).fetchone()
    if max_value:
        max_value = max_value[0]

    data_sub = cur.execute("SELECT id, descricao FROM categoria WHERE parent_id = ?", (parent_id,)).fetchall()
    sublist = [dict(row) for row in data_sub]

    return jsonify(sublist=sublist, parentid=parent_id, maxvalue=max_value)


@app.route("/fetchprod")
@login_required
def fetchprod():
    data_prod = cur.execute("SELECT * FROM produto").fetchall()
    data_sup = cur.execute("SELECT * FROM fornecedor").fetchall()

    productlist = [dict(row) for row in data_prod]
    supplierlist = [dict(row) for row in data_sup]

    return jsonify(productlist=productlist, supplierlist=supplierlist)


@app.route("/fetchpur")
@login_required
def fetchpur():
    query = request.args.get("query")

    data = cur.execute(
        "SELECT produto.produto_nome, SUM(compra_produto.quant) AS quant, compra_produto.preco_unit, fornecedor.fornecedor_nome " \
            "FROM compra_produto INNER JOIN produto ON compra_produto.produto_id = produto.id " \
                "INNER JOIN fornecedor ON compra_produto.fornecedor_id = fornecedor.id " \
                    "WHERE compras_id = ? GROUP BY produto.id", (query,)
        ).fetchall()
    
    purlist = [dict(row) for row in data]
    for row in purlist:
        row['total'] = row['quant'] * row['preco_unit']

    return jsonify(purlist=purlist, q=query)


@app.route("/category", methods=["GET", "POST"])
@login_required
def category():
    """Show history of transactions"""
    category_list = cur.execute("SELECT * FROM categoria WHERE parent_id IS NULL").fetchall()
    
    if request.method == "POST":
        category_id = request.form.get("id")
        print(category_id)
        cur.execute("DELETE FROM categoria WHERE id = ?", (category_id,))
        db.commit()

        flash("Item Removed")

    return render_template("category.html", category_list=category_list)


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    stocks_list = cur.execute("SELECT symbol, SUM(shares) AS shares FROM portfolio WHERE user_id = (?) GROUP BY symbol", user_id)

    if request.method == "POST":

        shares_max = 0
        for i in range(len(stocks_list)):
            if stocks_list[i]["symbol"] == request.form.get("symbol"):
                shares_max = stocks_list[i]["shares"]

        stock = lookup(request.form.get("symbol"))
        shares = request.form.get("shares")

        try:
            int(shares)
        except:
            return apology("invalid data type", 400)

        shares = int(shares)

        if shares < shares_max:
            shares *= (-1)
            purchase = shares * stock["price"]

            cur.execute("UPDATE users SET cash = cash - (?) WHERE id = (?)", (purchase, user_id,))

            dt = cur.execute("SELECT datetime()")
            cur.execute(
                "INSERT INTO portfolio (symbol, shares, price, user_id, operation, operation_time) VALUES(?, ?, ?, ?, ?, ?)",
                stock["symbol"], shares, stock["price"], user_id, "s", dt[0]["datetime()"])

            flash("Sold!")

            return redirect("/")

        else:
            return apology("you don't have that many shares", 400)

    else:
        return render_template("sell.html", stocks_list=stocks_list)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
