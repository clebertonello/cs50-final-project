import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import pandas_datareader.data as wd
from datetime import date

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

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session["user_id"]


    return render_template("index.html")

# source: https://tutorial101.blogspot.com/2021/02/python-flask-jquery-ajax-live-data.html
@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    """add product to database"""

    category_list = cur.execute("SELECT descricao FROM categoria WHERE parent_id IS NULL").fetchall()

    if request.method == "POST":
        user_id = session["user_id"]

        product_id = request.form.get("id")
        product_name = request.form.get("product_name")
        category_name = request.form.get("subcategory")

        category_id = cur.execute("SELECT id FROM categoria WHERE descricao = ?", (category_name,)).fetchone()[0]

        cur.execute("INSERT INTO produto_categoria (id_produto, id_categoria) VALUES (?, ?)", (product_id, category_id))
        cur.execute("INSERT INTO produto (id, produto_nome) VALUES (?, ?)", (product_id, product_name))
        db.commit()

        return redirect("/products")

    else:

        return render_template("products.html", category_list=category_list)

""" 
        stock = lookup(request.form.get("symbol"))
        if stock:
            shares = (request.form.get("shares"))
            try:
                int(shares)
            except:
                return apology("invalid data type", 400)

            shares = int(shares)

            if shares < 0:
                return apology("invalid data type", 400)

            purchase = shares * stock["price"]
            cash = cur.execute("SELECT cash FROM users WHERE id = (?)", user_id)

            if purchase > cash[0]['cash']:

                flash("You don't have enough Cash")
                return redirect("/products")

            else:

                cur.execute("UPDATE users SET cash = cash - (?) WHERE id = (?)", purchase, user_id)

                dt = cur.execute("SELECT datetime()")
                cur.execute(
                    "INSERT INTO portfolio (symbol, shares, price, user_id, operation, operation_time) VALUES(?, ?, ?, ?, ?, ?)",
                    stock["symbol"], shares, stock["price"], user_id, "b", dt[0]["datetime()"])

                flash("Bought!")

                return redirect("/")
        else:
            return apology("invalid stock", 400)
 """


@app.route("/fetchsubcat", methods=["GET", "POST"])
@login_required
def fetchsubcat():
    if request.method == 'GET':
        query = request.args.get('query')
        parent_id = cur.execute("SELECT id FROM categoria WHERE descricao = ?", (query,)).fetchone()[0]
        sublist = []
        data = cur.execute("SELECT descricao FROM categoria WHERE parent_id = ?", (parent_id,)).fetchall()
        
        for i in data:
            sublist.append(list(i))

        return jsonify(result=sublist)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    portfolio = cur.execute("SELECT symbol, shares, price, operation_time FROM portfolio WHERE user_id = (?)", user_id)

    return render_template("history.html", portfolio=portfolio)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock = lookup(request.form.get("symbol"))

        if stock:
            stock_text = ("A share of {}. ({}) costs {}.").format(stock['name'], stock['symbol'], usd(stock['price']))
            return render_template("quote.html", stock_text=stock_text)
        else:
            return apology("invalid stock", 400)

    else:
        return render_template("quote.html")


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
