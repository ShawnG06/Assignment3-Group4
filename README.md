Shawn:
I'm using postgres syntax for the most part?


This is Emil, here is a readme of the updates and what to expect:
# Update: Part 2 (validation + indexing) and Part 3 (insertion)

Files changed: `SQL/ex2.sql`, `SQL/ex3.sql`


Both files were run on a fresh PostgreSQL database and load without errors.

## How to run?

From the repo folder, as your normal user (not root):

    cd Assignment3-Group4
    dropdb --if-exists stock_trading && createdb stock_trading
    psql -d stock_trading -v ON_ERROR_STOP=1 -f SQL/ex2.sql
    psql -d stock_trading -v ON_ERROR_STOP=1 -f SQL/ex3.sql

`ex3.sql` expects an empty schema (it inserts its own setup rows), so recreate
the database before running it a second time.

## Part 2: Schema fixes (`ex2.sql`)

| Change | Why |
|---|---|
| `Holdings`: user foreign key moved from `tickerSymbol` to `email` | A ticker can never match a user's email, so every insert into `Holdings` would have failed |
| `AIAnalyses.analysisUUID`: `CHAR(36)` → `UUID DEFAULT gen_random_uuid()` | PostgreSQL rejects a foreign key between `CHAR(36)` and `UUID` (it's referenced by `RevenueAnalysis`) |
| `StockPrices`: `dailyMax > dailyMin` → `>=` | A day with no price movement (high = low) is valid |
| `Users.assignedDate`: added `DEFAULT CURRENT_DATE` | Role is assigned on insert unless a date is given |

## Part 2: Validation constraints added

| Table | Constraint | Rejects |
|---|---|---|
| `Users` | `chk_users_balance` | Negative balance |
| `Users` | `chk_users_email` | Email not shaped like `x@y.z` |
| `Users` | `uq_users_email_lower` (unique index) | `ALICE@example.com` when `alice@example.com` exists |
| `Company` | `uq_company_name` | Two companies with the same name |
| `Stocks` | `chk_stocks_ticker` | Lowercase ticker (`aapl`) |
| `Stocks` | `chk_stocks_exchange` | Exchange other than NYSE, NASDAQ, TSX, LSE |
| `AnnualRevenueReport` | `chk_revenue_currency` | Lowercase currency (`usd`) |

## Part 2: Indexes added

PostgreSQL indexes primary keys and `UNIQUE` columns automatically, but not
foreign keys. These cover foreign keys and common filters, matching the
Assignment 2 goal of fast retrieval of portfolios, historical prices,
company revenue and AI predictions.

| Index | Speeds up |
|---|---|
| `idx_users_role` | Users by role |
| `idx_stocks_company` | Stocks of a company |
| `idx_holdings_ticker` | Which users hold a stock |
| `idx_transactions_user_time` | A user's trade history, newest first |
| `idx_transactions_tick_time` | All trades of a stock, newest first |
| `idx_stockprices_date` | Prices of all stocks on a date |
| `idx_aianalyses_ticker_time` | Latest predictions for a stock |
| `idx_revenue_year` | Comparing companies' revenue in one year |
| `idx_revenueanalysis_revenue` | Analyses that used a revenue report |

Not indexed on purpose, because an existing key already starts with the column:
`Holdings(email)`, `StockPrices(tickerSymbol)`, `AnnualRevenueReport(companyId)`,
`RevenueAnalysis(analysisUUID)`.

## Part 3: Inserts (`ex3.sql`)

All three inserts go into `Transactions`, after setup rows for `Roles`,
`Company`, `Stocks`, `Users` and `StockPrices`.

1. **Single row** with a column list; `id` comes from its default.
2. **Multiple rows** in one statement, using the `DEFAULT` keyword for `id`.
3. **`INSERT ... SELECT`**: every TRADER buys 2 shares of each stock at the
   daily min of its latest trading date (correlated subquery).

Result: `SELECT * FROM Transactions` returns 7 rows. Every trade uses a
historic date and a price equal to that day's min or max.

## Notes for data generation (Part 4)

- `ex3.sql` uses company IDs 1–2, tickers `AAPL` / `RY`, and three
  `@example.com` emails. Generated data must avoid these keys, or the bulk
  load must run on a database without `ex3.sql` applied.
- Generate `StockPrices` before `Transactions`. Each trade should pick an
  existing (ticker, date) price row and use that date and a price within
  that day's min/max. Nothing in the schema enforces this, so the generator must.
- `Holdings` is not filled automatically from `Transactions`; the generator
  must insert holdings that are consistent with the generated trades.
- Tickers and currency codes must be uppercase, exchanges must be one of
  NYSE / NASDAQ / TSX / LSE, and company names must be unique.

## Still open

- **Triggers:** Part 2 says to "consider" triggers; **NONE ARE INCLUDED YET, IF YOU WANT ME TO DO THAT, TELL ME**.
  A price-range trigger on `Transactions` is the leading candidate.
- **`SQL/example.sql`:** uses MySQL syntax (`CREATE DATABASE IF NOT EXISTS`,
  `USE`) that fails in PostgreSQL.
- **Screenshots for the report:** the response to each `CREATE TABLE`, `\d` on
  all 10 tables, the three inserts, and `SELECT *`.