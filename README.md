# SE 3309 — Assignment 3: Stock Trading Database

## Group 4

- Shawn Gomez
- Emil Lokotosh
- Jolie Ma
- Saahil Patel
- Samuel Sharif

## Project overview

This project implements a PostgreSQL relational database for a stock trading and analysis application, building on the schema design completed in Assignments 1 and 2. The database stores user roles and accounts, companies, stock listings, holdings, transactions, historical stock prices, AI-generated analyses, annual revenue reports, and links between analyses and revenue data.

PostgreSQL was used in place of MySQL with instructor permission. The submission contains schema creation, sample INSERT demonstrations, substantial generated data, seven SELECT queries, three data modifications, two views, and an exported database dump.

## Repository contents

| Path | Purpose |
|---|---|
| `SQL/ex2.sql` | Database schema, constraints and indexes |
| `SQL/ex3.sql` | Setup records and three types of transaction INSERT operations |
| `SQL/ex5.sql` | Seven SELECT queries |
| `SQL/ex6.sql` | Three data modification statements |
| `SQL/ex7.sql` | Two views and SELECT demonstrations; modification-test commands documented in comments |
| `SQL/example.sql` | PostgreSQL database creation and `psql` connection example |
| `SRC/main.py` | Data generation entry point |
| `SRC/data.py` | Data fabrication functions |
| `SRC/database.py` | PostgreSQL connection and query helpers |
| `SRC/test_data.py` | Python unit tests for generation functions |
| `SRC/pyproject.toml`, `SRC/uv.lock` | Python dependency configuration |
| `SRC/.env.example` | Sample database connection settings (no credentials) |
| `DUMP/stock_db.sql` | Populated PostgreSQL database dump |
| `DESC/SE3309-Group4-Assignment3Report.pdf` | Report and SQL execution screenshots |

## Database setup and execution

The original schema and INSERT scripts were tested on a fresh PostgreSQL database. The following commands are for a **fresh test database only**; do not drop the populated database used for the assignment or run the sample inserts into it repeatedly.

From the repository root, with PostgreSQL tools installed and appropriate database credentials:

```bash
createdb -U postgres stock_trading
psql -U postgres -d stock_trading -v ON_ERROR_STOP=1 -f SQL/ex2.sql
psql -U postgres -d stock_trading -v ON_ERROR_STOP=1 -f SQL/ex3.sql
```

The `createdb` command is unnecessary if the database already exists. The `ex3.sql` script assumes the sample records have not yet been inserted. On Windows, these commands can be run in a terminal with PostgreSQL command-line tools available; the same SQL scripts can also be executed in pgAdmin's Query Tool, connected to the correct database.

The submitted populated database is available separately in `DUMP/stock_db.sql`; it includes the schema, data, and views. Do not execute `ex2.sql` or `ex7.sql` on top of a restored dump without first accounting for the objects already present.

## Exercise 2 — Schema implementation, corrections, validation, and indexing

The schema defines ten relations: `Roles`, `Company`, `Users`, `Stocks`, `Holdings`, `Transactions`, `StockPrices`, `AIAnalyses`, `AnnualRevenueReport`, and `RevenueAnalysis`.

### Corrections made to the schema

| Change | Reason |
|---|---|
| `Holdings`: user foreign key references `email` rather than `tickerSymbol` | A stock ticker cannot serve as a reference to a user's email; the earlier relationship would have prevented valid holding inserts. |
| `AIAnalyses.analysisUUID`: changed from `CHAR(36)` to `UUID DEFAULT gen_random_uuid()` | The referenced and referencing key columns must use compatible types; `RevenueAnalysis.analysisUUID` is also a UUID. |
| `StockPrices`: changed `dailyMax > dailyMin` to `dailyMax >= dailyMin` | A trading day with no price movement (high equal to low) is valid. |
| `Users.assignedDate`: added `DEFAULT CURRENT_DATE` | The role-assignment date can be populated automatically unless specified explicitly. |

### Validation constraints

| Table | Constraint | What it prevents or enforces |
|---|---|---|
| `Users` | `chk_users_balance` | Negative account balances |
| `Users` | `chk_users_email` | Emails that do not match the basic `x@y.z` shape |
| `Users` | `uq_users_email_lower` (unique index) | Emails differing only by letter case, such as `ALICE@example.com` and `alice@example.com` |
| `Company` | `uq_company_name` | Duplicate company names |
| `Stocks` | `chk_stocks_ticker` | Lowercase stock tickers |
| `Stocks` | `chk_stocks_exchange` | Exchanges other than NYSE, NASDAQ, TSX, or LSE |
| `AnnualRevenueReport` | `chk_revenue_currency` | Lowercase currency codes |

Additional constraints enforce positive transaction prices and quantities, nonnegative holdings and revenue values, valid BUY/SELL transactions, BUY/SELL/HOLD analysis recommendations, and stock-price ranges consistent with their daily minimum and maximum.

### Indexes and their purposes

PostgreSQL automatically creates indexes for primary keys and `UNIQUE` constraints, but not generally for foreign keys. Additional indexes cover relationships and commonly filtered or ordered attributes.

| Index | Purpose |
|---|---|
| `idx_users_role` | Retrieve users by role |
| `idx_stocks_company` | Retrieve stocks belonging to a company |
| `idx_holdings_ticker` | Find users holding a particular stock |
| `idx_transactions_user_time` | Retrieve a user's trades, newest first |
| `idx_transactions_tick_time` | Retrieve trades for a ticker, newest first |
| `idx_stockprices_date` | Retrieve prices across stocks for a date |
| `idx_aianalyses_ticker_time` | Retrieve the latest analysis predictions for a stock |
| `idx_revenue_year` | Compare company revenue in a given fiscal year |
| `idx_revenueanalysis_revenue` | Find analyses associated with a revenue report |

Additional single-column indexes were deliberately not created on `Holdings(email)`, `StockPrices(tickerSymbol)`, `AnnualRevenueReport(companyId)`, or `RevenueAnalysis(analysisUUID)` because their existing composite primary-key or unique indexes already begin with those columns.

No triggers were added. Exercise 2 asks students to consider triggers rather than explicitly requiring one; validation is enforced with the constraints shown above.

## Exercise 3 — Three types of INSERT operations

`SQL/ex3.sql` first inserts supporting records into `Roles`, `Company`, `Stocks`, `Users`, and `StockPrices`. Three different INSERT operations then target `Transactions`:

1. **Multiple-row `INSERT ... VALUES`:** inserts three BUY/SELL transactions with explicit column names and values. Transaction UUIDs come from the column default.
2. **`INSERT ... SELECT` with `CROSS JOIN` and a correlated subquery:** each sample user with the TRADER role buys two shares of each stock using the daily minimum from that stock's latest available trading date.
3. **`INSERT ... SELECT` with aggregation:** joins transactions to the latest stock-price entries, groups by user and ticker, uses a conditional `SUM` to identify positive net holdings, and generates additional SELL transactions with `HAVING`.

On a fresh schema containing just the sample setup records, the script produces **11 transaction records** in total (three explicit transactions, four from the second INSERT, and four from the aggregated INSERT).

These sample records use company IDs 1–2, ticker symbols `AAPL` and `RY`, and the sample `@example.com` emails. The generator must avoid conflicting keys when run on the same database.

## Exercise 4 — Data fabrication and relational integrity

The Python program in `SRC/` uses Faker and PostgreSQL connectivity to generate a substantial synthetic dataset. `main.py` coordinates the insertion sequence, while `data.py` implements the individual generators and `database.py` handles database connections.

The generator first creates roles, companies and users, then stocks and related holdings, prices, transactions, AI analyses and revenue reports. Generating the parent keys before dependent records allows foreign keys to refer to existing entities. Primary and unique keys prevent duplicates that violate schema constraints.

### Data-generation considerations

- Sample setup records from `ex3.sql` use company IDs 1–2, `AAPL`/`RY`, and three example emails. Bulk-generated identifiers must not collide with them.
- Historical stock-price records should precede transactions that reference those tickers. Ideally, trades should use an existing ticker/date price entry and a price within its day's range. **The provided generator currently fabricates transaction prices/timestamps independently, so this price alignment is a design consideration rather than an enforced guarantee.**
- `Holdings` is not automatically derived from `Transactions`; the generator populates it separately. The schema preserves valid user and ticker references but does not enforce transaction-to-holding reconciliation.
- Tickers and currency codes must be uppercase, exchanges are restricted to NYSE/NASDAQ/TSX/LSE, and company names must be unique.

The delivered database contains more than 3,000 users, 5,000 holdings, 5,000 transactions, 25,000 stock-price entries, and hundreds of AI analyses and revenue reports. The final PostgreSQL dump contains the records after Exercise 6 modifications.

### Python setup and tests

From `SRC/`, using the Python interpreter selected for the project:

```powershell
python -m pip install Faker "psycopg[binary]" python-dotenv
```

Create a local `.env` using `SRC/.env.example` as the template and configure the correct database host, port, name, user, and password. Do not commit actual credentials.

Run the existing unit tests from `SRC/`:

```powershell
python -m unittest discover -p "test_*.py" -v
```

The three provided unit tests passed during project validation. To generate records in a newly created database, run `python main.py` only after the schema and any required sample setup records have been established. Avoid rerunning the generator blindly on an already populated database.

## Exercise 5 — Seven SELECT queries

`SQL/ex5.sql` contains seven distinct queries demonstrating filtering and ordering, joins between companies and stocks, portfolio aggregation, multi-relation transaction analysis, `EXISTS`, correlated subqueries, and `GROUP BY`/`HAVING` for revenue comparisons. SQL statements and their PostgreSQL results are documented in the report.

## Exercise 6 — Data modification commands

`SQL/ex6.sql` contains three operations, executed after populating the database:

1. `DELETE` removes low-confidence SELL analyses where model accuracy is below 0.55.
2. `UPDATE` changes BUY recommendations below 0.60 model accuracy to HOLD.
3. `INSERT ... SELECT` links AI analyses to their companies' prior fiscal-year revenue reports, using PostgreSQL's `ON CONFLICT (analysisUUID, revenueId) DO NOTHING` to avoid duplicate relationships.

The recorded modifications deleted 19 analyses, updated 27 recommendations, and populated `RevenueAnalysis` with 4,508 relationships. The report separately illustrates the committed `ON CONFLICT` operation with a successful one-row test.

These modifications are not intended to be rerun without considering the current data and foreign-key references.

## Exercise 7 — Views and updatability

`SQL/ex7.sql` defines and queries:

- **`TSXStocks`** — filters `Stocks` to the Toronto Stock Exchange (`TSX`). Because it is based on one relation without aggregation, it is automatically updatable. `WITH CHECK OPTION` prevents modifications through the view that violate the exchange filter.
- **`UserPortfolioSummary`** — groups `Holdings` by user email and computes the holding count, total shares, and invested value. It is not automatically updatable because it uses aggregation and `GROUP BY`.

The report shows successful view creation and retrieval, a temporary insert through `TSXStocks` reflected in the base table, and the expected rejection of an update to `UserPortfolioSummary`.

## Report and submitted database

The formal report, including the SQL statements, editor responses, screenshots, and explanations, is in `DESC/SE3309-Group4-Assignment3Report.pdf`. The populated PostgreSQL database dump is in `DUMP/stock_db.sql`. The dump contains the database schema, data, constraints, indexes, and both views.
