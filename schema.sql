CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(100) NOT NULL,
    hash VARCHAR(100) NOT NULL,
    cash FLOAT NOT NULL DEFAULT 10000.00
);
CREATE TABLE stocks (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    symbol NOT NULL,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(100)
);
CREATE TABLE purchases (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    purchase_date TIMESTAMP NOT NULL,
    userID INT NOT NULL,
    shares INT NOT NULL,
    stock_id INT NOT NULL,
    stock_price FLOAT NOT NULL,
    total FLOAT NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
CREATE TABLE shares_owned (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    userID INT NOT NULL,
    stock_id INT NOT NULL,
    shares INT NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);