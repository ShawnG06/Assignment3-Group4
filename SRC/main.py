from data import (
    generate_companies,
    generate_revenue_reports,
    generate_roles,
    generate_stock_prices,
    generate_stocks,
    generate_users,
)
from database import connect


def main():
    with connect() as connection:
        print("Connected to DB")

        roles = generate_roles(connection)

        company_ids = generate_companies(connection, count=80)

        generate_users(connection, roles, count=1000)

        tickers = generate_stocks(
            connection,
            company_ids,
            count=100,
        )

        generate_stock_prices(connection, tickers, days=250)

        generate_revenue_reports(connection, company_ids)


if __name__ == "__main__":
    main()
