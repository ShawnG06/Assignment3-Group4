-- Query 1 (basic selection): stocks and their exchanges.
SELECT tickerSymbol, exchange
FROM Stocks
WHERE exchange IS NOT NULL
ORDER BY tickerSymbol
FETCH FIRST 20 ROWS ONLY;

-- Query 2 (join): list stocks with their company and sector.
SELECT s.tickerSymbol, s.exchange, c.companyName, c.sector
FROM Stocks AS s
JOIN Company AS c
  ON c.companyId = s.companyId
WHERE s.exchange IN ('NYSE', 'NASDAQ', 'TSX', 'LSE')
ORDER BY c.companyName, s.tickerSymbol
FETCH FIRST 20 ROWS ONLY;

-- Query 3 (GROUP BY): summarize each user's portfolio holdings.
SELECT h.email,
       COUNT(*) AS numberOfStocks,
       SUM(h.quantity) AS totalShares,
       SUM(h.quantity * h.averagePrice) AS investedValue
FROM Holdings AS h
WHERE h.quantity > 0
GROUP BY h.email
ORDER BY investedValue DESC
FETCH FIRST 20 ROWS ONLY;

-- Query 4 (multiple joins): recent transactions with user and company details.
SELECT t.id, t.email, u.roleName, t.transactionType, t.quantity, t.price,
       t.createdAt, s.tickerSymbol, c.companyName
FROM Transactions AS t
JOIN Stocks AS s
  ON s.tickerSymbol = t.tickerSymbol
JOIN Company AS c
  ON c.companyId = s.companyId
JOIN Users AS u
  ON u.email = t.email
WHERE t.transactionType IN ('BUY', 'SELL')
ORDER BY t.createdAt DESC
FETCH FIRST 20 ROWS ONLY;

-- Query 5 (EXISTS): stocks that have at least one AI analysis, with their company.
SELECT c.companyId, c.companyName, s.tickerSymbol
FROM Company AS c
JOIN Stocks AS s
  ON s.companyId = c.companyId
WHERE EXISTS (
    SELECT 1
    FROM AIAnalyses AS a
    WHERE a.tickerSymbol = s.tickerSymbol
)
ORDER BY c.companyName, s.tickerSymbol
FETCH FIRST 20 ROWS ONLY;

-- Query 6 (correlated subquery): prices at or above that stock's average close.
SELECT sp.tickerSymbol, sp.tradingDate, sp.closingPrice
FROM StockPrices AS sp
WHERE sp.closingPrice >= (
    SELECT AVG(sp2.closingPrice)
    FROM StockPrices AS sp2
    WHERE sp2.tickerSymbol = sp.tickerSymbol
)
ORDER BY sp.tickerSymbol, sp.tradingDate DESC
FETCH FIRST 20 ROWS ONLY;

-- Query 7 (GROUP BY + HAVING): sectors with more than one reporting company.
SELECT c.sector,
       COUNT(DISTINCT c.companyId) AS companies,
       AVG(ar.totalRevenue) AS avgRevenue
FROM Company AS c
JOIN AnnualRevenueReport AS ar
  ON ar.companyId = c.companyId
GROUP BY c.sector
HAVING COUNT(DISTINCT c.companyId) > 1
ORDER BY avgRevenue DESC
FETCH FIRST 20 ROWS ONLY;