import os
import datetime
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    # define userId
    id = session["user_id"]
    # set expected data structure
    stocks = []
    # set variable for total value of stock shares owned
    total = 0
    sharesList = db.execute("SELECT * FROM shares_owned WHERE userId = ?", id)
    for share in sharesList:
        row = db.execute(
            "SELECT symbol, name FROM stocks WHERE id = ?", share["stock_id"])
        current = lookup(row[0]["symbol"])
        price = current["price"]
        shares = share["shares"]
        dict = {}
        dict["name"] = row[0]["name"]
        dict["shares"] = shares
        dict["price"] = usd(price)
        product = round(price * 100 * shares * 100, 2) / 10000
        print(usd(product))
        dict["product"] = usd(product)
        stocks.append(dict)
        total = round(total * 100 + product * 100, 2) / 100
    # get user cash balance
    balanceList = db.execute("SELECT cash FROM users WHERE id = ?", id)
    balance = balanceList[0]["cash"]
    total = round(total * 100 + balance * 100, 2) / 100

    return render_template("index.html", stocks=stocks, balance=usd(balance), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("buy.html")

    # Get symbol
    symbol = request.form.get("symbol")
    # Ensure symbol was submitted
    if not symbol:
        return apology("must provide symbol", 400)

    # Ensure symbol is valid
    stockLookup = lookup(symbol)
    if not stockLookup:
        return apology("must provide valid symbol", 400)

    # Get shares
    shares = request.form.get("shares")
    # Ensure # of shares was submitted
    if not shares:
        return apology("must provide number of shares", 400)
    # Ensure # of shares is a positive integer
    if not shares.isnumeric():
        return apology("must provide a positive number", 400)
    # convert shares str to int
    shares = float(shares)
    # Ensure positive # of shares was submitted
    if not shares > 0:
        return apology("must provide a positive number", 400)

    stockId = 0
    # get stock id based on symbol
    stockIdList = db.execute("SELECT id FROM stocks WHERE symbol = ?", symbol)
    if not len(stockIdList) == 0:
        stockId = stockIdList[0]["id"]
    else:
        return apology("must provide a valid symbol", 400)

    # check if user can afford the purchase
    id = session["user_id"]
    userCashList = db.execute("SELECT cash FROM users WHERE id = ?", id)
    if not len(userCashList) == 0:
        userCash = userCashList[0]["cash"]
        stockPrice = stockLookup["price"]

    total = round(shares * 100 * stockPrice * 100, 2) / 10000
    name = stockLookup["name"]
    # enable purchase
    if userCash > total:
        # update user's cash balance
        balance = round(userCash * 100 - total * 100, 2) / 100
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, id)

        # record transaction in transactions table
        purchaseDate = datetime.datetime.now()
        db.execute("INSERT INTO transactions (purchase_date, userID, shares, stock_id, stock_price, total) VALUES (?, ?, ?, ?, ?, ?)",
                   purchaseDate, id, shares, stockId, stockPrice, total)

        # check if stock exists in stocks table and add if not
        isStock = db.execute("SELECT * FROM stocks WHERE symbol = ?", symbol)
        if len(isStock) == 0:
            db.execute(
                "INSERT INTO stocks (symbol, name) VALUES (?, ?)", symbol, name)

        # check if user exists in shares_owned table
        userList = db.execute(
            "SELECT * FROM shares_owned WHERE userId = ?", id)
        if not len(userList) == 0:
            # find element
            index = find(userList, "stock_id", stockId)
            # check if user has shares of specific stock
            if index >= 0:
                userShares = userList[index]["shares"]
                shares = shares + userShares
                db.execute(
                    "UPDATE shares_owned SET shares= ? WHERE userId = ? AND stock_id = ?", shares, id, stockId)
            else:
                db.execute(
                    "INSERT INTO shares_owned (userID, stock_id, shares) VALUES (?, ?, ?)", id, stockId, shares,)
        else:
            db.execute(
                "INSERT INTO shares_owned (userID, stock_id, shares) VALUES (?, ?, ?)", id, stockId, shares,)
        # Redirect user to home page
        return redirect("/")

    # deny purchase
    else:
        return apology("not enough cash for purchase", 400)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # define userId
    id = session["user_id"]
    # set expected data structure
    userTransactions = []

    # get transactions based on user
    transactions = db.execute(
        "SELECT * FROM transactions WHERE userID = ?", id)
    # set dict for each transaction and append to userTransactions
    for transaction in transactions:
        dict = {}
        dict["type"] = transaction["type"]
        symbol = db.execute(
            "SELECT symbol FROM stocks WHERE id = ?", transaction["stock_id"])
        dict["symbol"] = symbol[0]["symbol"]
        amount = usd(transaction["total"])
        dict["amount"] = amount
        dict["shares"] = transaction["shares"]
        dt_str = transaction["purchase_date"]
        dt_obj = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dict["date"] = dt_obj.strftime('%d-%b-%Y')
        dict["time"] = dt_obj.strftime('%-H:%M:%S')
        userTransactions.append(dict)

    return render_template("history.html", transactions=userTransactions)
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

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
    """Get stock quote."""
    # User reached route via GET (as by clicking a link)
    if request.method == "GET":
        return render_template("quote.html")

    symbol = request.form.get("symbol")
    # Ensure symbol was submitted
    if not symbol:
        return apology("must provide symbol", 400)
    # Get values from looking up symbol
    stockLookup = lookup(symbol)
    # Ensure lookup successful
    if not stockLookup:
        return apology("invalid symbol", 400)

    # Direct user to quoted page
    return render_template("quoted.html", name=stockLookup["name"], price=usd(stockLookup["price"]), symbol=stockLookup["symbol"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)
        # Check passwords for match
        elif not confirmation == password:
            return apology("password must match", 400)
        # Query database for username
        elif db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("username already exists", 400)
        # Add user to database
        else:
            hash = generate_password_hash(
                password, method='pbkdf2:sha256', salt_length=8)
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # USER REACHED ROUTE ON GET REQUEST:

    # get user id
    id = session["user_id"]
    # get user's shares info
    sharesList = db.execute("SELECT * FROM shares_owned WHERE userID = ?", id)

    # get stock symbols
    userShares = []
    for share in sharesList:
        dict = {}
        # get symbol
        stockId = share["stock_id"]
        stockSymbolList = db.execute(
            "SELECT symbol FROM stocks WHERE id = ?", stockId)
        stockSymbol = stockSymbolList[0]["symbol"]
        # add to dict key/val pair for symbol
        dict["symbol"] = stockSymbol
        # get shares
        shares = share["shares"]
        # add to dict key/val pair for shares
        dict["shares"] = shares
        # append dict to userShares list
        userShares.append(dict)

    if request.method == "GET":
        return render_template("sell.html", userShares=userShares)

    # USER REACHED ROUTE ON POST REQUEST:

    # get selected option value
    symbol = request.form.get("select")
    # check if option is valid symbol
    validStock = db.execute(
        "SELECT id, symbol FROM stocks WHERE symbol = ?", symbol)
    if not validStock:
        return apology("Select a valid stock")

    # get shares input
    sharesToSell = int(request.form.get("shares"))
    # Ensure # of shares was submitted
    if not sharesToSell:
        return apology("must provide number of shares", 400)
    # Ensure positive # of shares was submitted
    elif not sharesToSell > 0:
        return apology("must provide a positive number for shares", 400)

    # UPDATE SHARES_OWNED TABLE:
    # get user's share info
    stockId = validStock[0]["id"]
    userShare = db.execute(
        "SELECT * FROM shares_owned WHERE userID = ? AND stock_id = ?", id, stockId)

    # check shares do not exceed owned shares
    owned_shares = userShare[0]["shares"]
    if sharesToSell > owned_shares:
        return apology("You do not have enough shares", 400)

    # update users cash
    stockLookup = lookup(validStock[0]["symbol"])
    stockPrice = stockLookup["price"]
    total = round((stockPrice * 100) * (sharesToSell * 100), 2) / 10000
    cashQuery = db.execute("SELECT cash FROM users WHERE id = ?", id)
    balance = cashQuery[0]["cash"]
    cash = round((balance * 100) + (total * 100), 2) / 100
    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, id)

    # update transactions table
    purchaseDate = datetime.datetime.now()
    db.execute("INSERT INTO transactions (purchase_date, userID, shares, stock_id, stock_price, total, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
               purchaseDate, id, sharesToSell, stockId, stockPrice, total, "Sell")

    # if shares matches owned shares, remove stock row from shares owned table
    if sharesToSell == owned_shares:
        db.execute(
            "DELETE FROM shares_owned WHERE userID = ? AND stock_id = ?", id, stockId)
    # update owned shares
    shares = owned_shares - sharesToSell
    db.execute(
        "UPDATE shares_owned SET shares = ? WHERE userID = ? AND stock_id = ?", shares, id, stockId)

    # Redirect user to home page
    return redirect("/")


@app.route("/search")
def search():
    input = request.args.get("q")
    # send q to database and get all stocks LIKE q
    stocks = db.execute(
        "SELECT * FROM stocks WHERE symbol LIKE ? LIMIT ?", input + "%", 100)

    if not stocks:
        return stocks

    # iterate through list for exact match to input
    index = find(stocks, "symbol", input)
    selectedStock = stocks[index]

    # set expected data structure for response object
    data = []
    # if query contains multiple items and exact match to input
    if len(stocks) > 1 and index >= 0:
        dict = {}
        dict = setDict(selectedStock)
        data.append(dict)
        # slice off duplicate stock (already in selectedStock)
        stocks.pop(0)
        for stock in stocks:
            data.append(stock)
        return data
    # if query contains multiple items
    if len(stocks) > 1:
        return stocks

    # if only one in query, lookup stock for price
    elif len(stocks) == 1:
        stock = stocks[0]
        dict = setDict(stock)
        data.append(dict)
        return data


@app.route("/shares")
@login_required
def getShares():
    id = session["user_id"]
    symbol = request.args.get("q")
    # get symbol id
    symbol_idList = db.execute(
        "SELECT id FROM stocks WHERE symbol = ?", symbol)
    symbol_id = symbol_idList[0]["id"]
    sharesList = db.execute(
        "SELECT shares FROM shares_owned WHERE userID = ? AND stock_id = ?", id, symbol_id)
    shares = sharesList[0]["shares"]
    print(shares)
    return [shares]


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def setDict(stock):
    dict = {}
    symbol = stock["symbol"]
    stockLookup = lookup(symbol)
    name = stock["name"]
    price = stockLookup["price"]
    dict['symbol'] = symbol
    dict['name'] = name
    dict['price'] = price
    return dict
