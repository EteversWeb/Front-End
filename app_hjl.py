import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd, find_stock_info, create_user_info

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]
    transactions = db.execute("SELECT * FROM transactions WHERE username=?", user["username"])
    user_info = create_user_info(user, transactions)
    return render_template("index.html",user_info=user_info)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("The quote does not exist", 403)
        
        shares = request.form.get("shares")
        if int(shares) <= 0:
            return apology("Shares must be a positive integer")
        
        user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]
        if user["cash"] < quote['price'] * int(shares):
            return apology("You don't have enough money")
        
        db.execute("INSERT INTO transactions (username, purchase_time, symbol, shares, price) VALUES (?, ?, ?, ?, ?)", user["username"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), quote["symbol"], int(shares), quote["price"])
        db.execute("UPDATE users SET cash = ? WHERE username = ?", (user["cash"]-quote['price'] * int(shares)), user["username"])
        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]
    transactions = db.execute("SELECT * FROM transactions WHERE username=?", user["username"])
    """Show history of transactions"""
    return render_template("history.html",transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("you have to enter right symbol")
        return render_template("quoted.html",quote = quote)
    
    else:
        return render_template("quote.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = db.execute("SELECT * FROM users")
        username = request.form.get("username")

        if not username:
            return apology("invalid username", 403)
        elif any(user['username'] == username for user in users):
            return apology("username already exists", 403)
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if not password1 or not password2:
            return apology("must provide password", 403)
        elif password1 != password2:
            return apology("both password must be same", 403)

        password = generate_password_hash(password1, method='pbkdf2', salt_length=16)
        db.execute("INSERT INTO users (username, hash, cash) VALUES (?, ?, 10000)", username, password)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("The quote does not exist", 403)
        
        user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]
        transactions = db.execute("SELECT * FROM transactions WHERE username=?", user["username"])
        user_info = create_user_info(user, transactions)
        stock_info = find_stock_info(user_info, quote["symbol"])
        shares = request.form.get("shares")
        if stock_info == -1:
            return apology("you don't have that stock")
        if int(shares) <= 0:
            return apology("Shares must be a positive integer")
        if stock_info["shares"] < int(shares):
            return apology("you don't have enough stock")
        
        db.execute("INSERT INTO transactions (username, purchase_time, symbol, shares, price) VALUES (?, ?, ?, ?, ?)", user["username"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), quote["symbol"], int(shares)*-1, quote["price"])
        db.execute("UPDATE users SET cash = ? WHERE username = ?", (user["cash"]+quote['price'] * int(shares)), user["username"])
        return redirect("/")
    else:
        return render_template("sell.html")
    return apology("TODO")


    