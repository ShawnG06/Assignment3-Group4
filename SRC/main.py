from data import (
    generate_companies,
    generate_ai_analyses,
    generate_holdings,
    generate_revenue_reports,
    generate_roles,
    generate_stock_prices,
    generate_stocks,
    generate_transactions,
    generate_users,
)
from database import connect


def main():
    with connect() as connection:
        print("Connected to DB")

        roles = generate_roles(connection)

        company_ids = generate_companies(connection, count=80)

        user_emails = generate_users(connection, roles, count=3000)

        tickers = generate_stocks(
            connection,
            company_ids,
            count=100,
        )
        generate_holdings(connection, user_emails, tickers, count=5000)
        generate_stock_prices(connection, tickers, days=250)
        generate_transactions(connection, user_emails, tickers, count=5000)
        generate_ai_analyses(connection, tickers, count=500)

        generate_revenue_reports(connection, company_ids)


if __name__ == "__main__":
    main()
