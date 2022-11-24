CREATE DATABASE finance;

CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00);
CREATE TABLE sqlite_sequence(name,seq);
CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
    symbol NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT);

CREATE TABLE purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        purchase_date TIMESTAMP NOT NULL,
        userID INTEGER NOT NULL,
        shares INTEGER NOT NULL,
        stock_id INTEGER NOT NULL,
        stock_price REAL NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (userID) REFERENCES users(id),
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    );

CREATE TABLE shares_owned (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    shares INTEGER NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);