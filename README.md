# Stock Trader
#### Link: http://stocktrader-env.eba-fqy4b2qm.ap-northeast-1.elasticbeanstalk.com
In short, this is a Python Flask application that is hosted by AWS elastic beanstalk and is using AWS RDS for the database.
This stock trader app registers users. Each user gets an initial $10,000 to "spend".
Users can: get a quote, buy, or sell stocks. 
My special features are:
    --- A dynamic search written in javascript that calls an api on the backend to return the names of stocks that have matching characters along with the prices. 
    Then the name, price, number of shares selected, and total cost of the stock will display in the table. 
    Once there is an exact match, the buy button is enabled. Changing the number of shares will manipulate the total cost of the purchase.
    --- In the sell page, there is a dropdown of the stocks the user owns. The user can only select up to the displayed max shares to sell, which is the number of shares the user owns.
    --- The history page tables the user's transactions and displays the "buys" in red, indicating negative transactions, and the "sells" in green, indicating positive transactions.

Note: Deploying, setting up a remote db, and the use of pymysql were not part of the assignment

The base assignment was as follows: 
### cs_solutions_finance_app

Implement a website via which users can “buy” and “sell” stocks.

You’re about to implement C$50 Finance, a web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you buy (okay, “buy”) and sell (okay, “sell”) stocks by querying IEX for stocks’ prices.

Indeed, IEX lets you download stock quotes via their API (application programming interface) using URLs like https://cloud.iexapis.com/stable/stock/nflx/quote?token=API_KEY. Notice how Netflix’s symbol (NFLX) is embedded in this URL; that’s how IEX knows whose data to return. That link won’t actually return any data because IEX requires you to use an API key (more about that in a bit), but if it did, you’d see a response in JSON (JavaScript Object Notation) format like this:

{
"avgTotalVolume": 4329597,
"calculationPrice": "tops",
"change": 1.21,
"changePercent": 0.00186,
"closeSource": "official",
"companyName": "NetFlix Inc",
"currency": "USD",
"iexAskPrice": 662.59,
"iexAskSize": 8080,
"iexBidPrice": 652.65,
"iexBidSize": 102,
"iexClose": 652.66,
"iexCloseTime": 1636479523133,
"iexLastUpdated": 1636479523133,
"iexMarketPercent": 0.03419734093274243,
"iexOpen": 652.66,
"iexOpenTime": 1636479523133,
"iexRealtimePrice": 652.66,
"iexRealtimeSize": 30,
"iexVolume": 43968,
"lastTradeTime": 1636479523133,
"latestPrice": 652.66,
"latestSource": "IEX real time price",
"latestTime": "12:38:43 PM",
"latestUpdate": 1636479523133,
"marketCap": 288341929921,
"openSource": "official",
"peRatio": 58.85,
"previousClose": 651.45,
"previousVolume": 2887523,
"primaryExchange": "NASDAQ",
"symbol": "NFLX",
"week52High": 690.97,
"week52Low": 463.41,
"ytdChange": 0.2066202315388457
}
Notice how, between the curly braces, there’s a comma-separated list of key-value pairs, with a colon separating each key from its value.

Configuring
Before getting started on this assignment, we’ll need to register for an API key in order to be able to query IEX’s data. To do so, follow these steps:

Visit iexcloud.io/cloud-login#/register/.
Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.
Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.
Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.
Copy the key that appears under the Token column (it should begin with pk\_).
In your terminal window, execute:
$ export API_KEY=value
where value is that (pasted) value, without any space immediately before or after the =. You also may wish to paste that value in a text document somewhere, in case you need it again later.

Running
Start Flask’s built-in web server (within finance/):

$ flask run
Visit the URL outputted by flask to see the distribution code in action. You won’t be able to log in or register, though, just yet!

Within finance/, run sqlite3 finance.db to open finance.db with sqlite3. If you run .schema in the SQLite prompt, notice how finance.db comes with a table called users. Take a look at its structure (i.e., schema). Notice how, by default, new users will receive $10,000 in cash. But if you run SELECT \* FROM users;, there aren’t (yet!) any users (i.e., rows) therein to browse.

Another way to view finance.db is with a program called phpLiteAdmin. Click on finance.db in your codespace’s file browser, then click the link shown underneath the text “Please visit the following link to authorize GitHub Preview”. You should see information about the database itself, as well as a table, users, just like you saw in the sqlite3 prompt with .schema.

Understanding
app.py
Open up app.py. Atop the file are a bunch of imports, among them CS50’s SQL module and a few helper functions. More on those soon.

After configuring Flask, notice how this file disables caching of responses (provided you’re in debugging mode, which you are by default in your code50 codespace), lest you make a change to some file but your browser not notice. Notice next how it configures Jinja with a custom “filter,” usd, a function (defined in helpers.py) that will make it easier to format values as US dollars (USD). It then further configures Flask to store sessions on the local filesystem (i.e., disk) as opposed to storing them inside of (digitally signed) cookies, which is Flask’s default. The file then configures CS50’s SQL module to use finance.db.

Thereafter are a whole bunch of routes, only two of which are fully implemented: login and logout. Read through the implementation of login first. Notice how it uses db.execute (from CS50’s library) to query finance.db. And notice how it uses check_password_hash to compare hashes of users’ passwords. Also notice how login “remembers” that a user is logged in by storing his or her user_id, an INTEGER, in session. That way, any of this file’s routes can check which user, if any, is logged in. Finally, notice how once the user has successfully logged in, login will redirect to "/", taking the user to their home page. Meanwhile, notice how logout simply clears session, effectively logging a user out.

Notice how most routes are “decorated” with @login_required (a function defined in helpers.py too). That decorator ensures that, if a user tries to visit any of those routes, he or she will first be redirected to login so as to log in.

Notice too how most routes support GET and POST. Even so, most of them (for now!) simply return an “apology,” since they’re not yet implemented.

helpers.py
Next take a look at helpers.py. Ah, there’s the implementation of apology. Notice how it ultimately renders a template, apology.html. It also happens to define within itself another function, escape, that it simply uses to replace special characters in apologies. By defining escape inside of apology, we’ve scoped the former to the latter alone; no other functions will be able (or need) to call it.

Next in the file is login_required. No worries if this one’s a bit cryptic, but if you’ve ever wondered how a function can return another function, here’s an example!

Thereafter is lookup, a function that, given a symbol (e.g., NFLX), returns a stock quote for a company in the form of a dict with three keys: name, whose value is a str, the name of the company; price, whose value is a float; and symbol, whose value is a str, a canonicalized (uppercase) version of a stock’s symbol, irrespective of how that symbol was capitalized when passed into lookup.

Last in the file is usd, a short function that simply formats a float as USD (e.g., 1234.56 is formatted as $1,234.56).

requirements.txt
Next take a quick look at requirements.txt. That file simply prescribes the packages on which this app will depend.

static/
Glance too at static/, inside of which is styles.css. That’s where some initial CSS lives. You’re welcome to alter it as you see fit.

templates/
Now look in templates/. In login.html is, essentially, just an HTML form, stylized with Bootstrap. In apology.html, meanwhile, is a template for an apology. Recall that apology in helpers.py took two arguments: message, which was passed to render_template as the value of bottom, and, optionally, code, which was passed to render_template as the value of top. Notice in apology.html how those values are ultimately used! And here’s why 0:-)

Last up is layout.html. It’s a bit bigger than usual, but that’s mostly because it comes with a fancy, mobile-friendly “navbar” (navigation bar), also based on Bootstrap. Notice how it defines a block, main, inside of which templates (including apology.html and login.html) shall go. It also includes support for Flask’s message flashing so that you can relay messages from one route to another for the user to see.

Specification
register
Complete the implementation of register in such a way that it allows a user to register for an account via a form.

Require that a user input a username, implemented as a text field whose name is username. Render an apology if the user’s input is blank or the username already exists.
Require that a user input a password, implemented as a text field whose name is password, and then that same password again, implemented as a text field whose name is confirmation. Render an apology if either input is blank or the passwords do not match.
Submit the user’s input via POST to /register.
INSERT the new user into users, storing a hash of the user’s password, not the password itself. Hash the user’s password with generate_password_hash Odds are you’ll want to create a new template (e.g., register.html) that’s quite similar to login.html.
Once you’ve implemented register correctly, you should be able to register for an account and log in (since login and logout already work)! And you should be able to see your rows via phpLiteAdmin or sqlite3.

quote
Complete the implementation of quote in such a way that it allows a user to look up a stock’s current price.

Require that a user input a stock’s symbol, implemented as a text field whose name is symbol.
Submit the user’s input via POST to /quote.
Odds are you’ll want to create two new templates (e.g., quote.html and quoted.html). When a user visits /quote via GET, render one of those templates, inside of which should be an HTML form that submits to /quote via POST. In response to a POST, quote can render that second template, embedding within it one or more values from lookup.
buy
Complete the implementation of buy in such a way that it enables a user to buy stocks.

Require that a user input a stock’s symbol, implemented as a text field whose name is symbol. Render an apology if the input is blank or the symbol does not exist (as per the return value of lookup).
Require that a user input a number of shares, implemented as a field whose name is shares. Render an apology if the input is not a positive integer.
Submit the user’s input via POST to /buy.
Upon completion, redirect the user to the home page.
Odds are you’ll want to call lookup to look up a stock’s current price.
Odds are you’ll want to SELECT how much cash the user currently has in users.
Add one or more new tables to finance.db via which to keep track of the purchase. Store enough information so that you know who bought what at what price and when.
Use appropriate SQLite types.
Define UNIQUE indexes on any fields that should be unique.
Define (non-UNIQUE) indexes on any fields via which you will search (as via SELECT with WHERE).
Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price.
You don’t need to worry about race conditions (or use transactions).
Once you’ve implemented buy correctly, you should be able to see users’ purchases in your new table(s) via phpLiteAdmin or sqlite3.

index
Complete the implementation of index in such a way that it displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

Odds are you’ll want to execute multiple SELECTs. Depending on how you implement your table(s), you might find GROUP BY HAVING SUM and/or WHERE of interest.
Odds are you’ll want to call lookup for each stock.
sell
Complete the implementation of sell in such a way that it enables a user to sell shares of a stock (that he or she owns).

Require that a user input a stock’s symbol, implemented as a select menu whose name is symbol. Render an apology if the user fails to select a stock or if (somehow, once submitted) the user does not own any shares of that stock.
Require that a user input a number of shares, implemented as a field whose name is shares. Render an apology if the input is not a positive integer or if the user does not own that many shares of the stock.
Submit the user’s input via POST to /sell.
Upon completion, redirect the user to the home page.
You don’t need to worry about race conditions (or use transactions).
history
Complete the implementation of history in such a way that it displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.

For each row, make clear whether a stock was bought or sold and include the stock’s symbol, the (purchase or sale) price, the number of shares bought or sold, and the date and time at which the transaction occurred.
You might need to alter the table you created for buy or supplement it with an additional table. Try to minimize redundancies.
personal touch
Implement at least one personal touch of your choice:

Allow users to change their passwords.
Allow users to add additional cash to their account.
Allow users to buy more shares or sell shares of stocks they already own via index itself, without having to type stocks’ symbols manually.
Require users’ passwords to have some number of letters, numbers, and/or symbols.
Implement some other feature of comparable scope.
