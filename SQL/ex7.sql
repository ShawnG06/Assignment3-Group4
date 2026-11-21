
-- Exercise 7: View 1
-- Updatable view of Toronto Stock Exchange stocks.

CREATE VIEW TSXStocks AS
SELECT tickerSymbol, companyId, exchange
FROM Stocks
WHERE exchange = 'TSX'
WITH CHECK OPTION;

-- Query involving View 1
SELECT tickerSymbol, companyId, exchange
FROM TSXStocks
ORDER BY tickerSymbol
FETCH FIRST 10 ROWS ONLY;


-- Exercise 7: View 2
-- Non-updatable view that summarizes user portfolios.

CREATE VIEW UserPortfolioSummary AS
SELECT
    email,
    COUNT(*) AS stockCount,
    SUM(quantity) AS totalShares,
    SUM(quantity * averagePrice) AS totalInvested
FROM Holdings
GROUP BY email;

-- Query involving View 2
SELECT
    email,
    stockCount,
    totalShares,
    totalInvested
FROM UserPortfolioSummary
ORDER BY totalInvested DESC
FETCH FIRST 10 ROWS ONLY;

-- Exercise 7: Modification Tests
-- Execute these tests individually in pgAdmin.
-- Do not execute this section with the initial CREATE VIEW statements.

-- Test 1: Updatable view
-- BEGIN;
-- INSERT INTO TSXStocks (tickerSymbol, companyId, exchange)
-- VALUES ('VTEST', 2, 'TSX');
-- SELECT * FROM TSXStocks WHERE tickerSymbol = 'VTEST';
-- SELECT * FROM Stocks WHERE tickerSymbol = 'VTEST';
-- ROLLBACK;

-- Test 2: Non-updatable view
-- UPDATE UserPortfolioSummary
-- SET totalInvested = 0
-- WHERE email = (
--     SELECT MIN(email)
--     FROM UserPortfolioSummary
-- );
-- Expected: PostgreSQL rejects this update.