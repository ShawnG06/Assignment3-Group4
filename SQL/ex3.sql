INSERT INTO Roles VALUES ('TRADER'), ('ADMIN');

INSERT INTO Company VALUES
	(1, 'Apple Inc.', 'Technology'),
	(2, 'Royal Bank of Canada', 'Financials');

INSERT INTO Stocks VALUES
	('AAPL', 1, 'NASDAQ'),
	('RY', 2, 'TSX');

INSERT INTO Users (email, passwordHash, balance, roleName) VALUES
	('alice@example.com', 'hash1', 10000, 'TRADER'),
	('bob@example.com',   'hash2',  5000, 'TRADER'),
	('carol@example.com', 'hash3',     0, 'ADMIN');

INSERT INTO StockPrices VALUES
	('AAPL', '2026-11-18', 188.00, 190.00, 191.20, 187.50),
	('AAPL', '2026-11-19', 190.10, 192.40, 193.00, 189.80),
	('RY',   '2026-11-18', 140.00, 141.25, 141.90, 139.60),
	('RY',   '2026-11-19', 141.30, 140.80, 142.00, 140.10);

INSERT INTO Transactions (email, tickerSymbol, quantity, createdAt, transactionType, price)
VALUES ('alice@example.com', 'AAPL', 10, TIMESTAMP '2026-11-18 09:45:00', 'BUY', 187.50);

INSERT INTO Transactions (id, email, tickerSymbol, quantity, createdAt, transactionType, price)
VALUES
	(DEFAULT, 'bob@example.com',   'RY',   5, TIMESTAMP '2026-11-18 10:30:00', 'BUY',  139.60),
	(DEFAULT, 'alice@example.com', 'AAPL', 4, TIMESTAMP '2026-11-19 14:05:00', 'SELL', 193.00);

INSERT INTO Transactions (email, tickerSymbol, quantity, createdAt, transactionType, price)
SELECT u.email, sp.tickerSymbol, 2, CAST(sp.tradingDate AS TIMESTAMP), 'BUY', sp.dailyMin
FROM Users u
CROSS JOIN StockPrices sp
WHERE u.roleName = 'TRADER'
  AND sp.tradingDate = (SELECT MAX(sp2.tradingDate)
                        FROM StockPrices sp2
                        WHERE sp2.tickerSymbol = sp.tickerSymbol);

SELECT * FROM Transactions;
