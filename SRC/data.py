import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker

from database import fetch_all, fetch_one, insert_data

fake = Faker()

random.seed(42)
Faker.seed(42)


def generate_roles(connection):
    records = [("Admin",), ("Trader",), ("Analyst",)]

    query = """

        INSERT INTO Roles(roleName)
        VALUES(%s)
        ON CONFLICT (roleName) DO NOTHING
    """

    count = insert_data(connection, query, records)

    print(f"Roles: {count} records inserted")

    return [record[0] for record in records]


def generate_companies(connection, count=80):
    sectors = [
        "Technology",
        "Healthcare",
        "Energy",
        "Finance",
        "Industrials",
        "Communication",
    ]

    start_id = (
        fetch_one(
            connection,
            """
        SELECT COALESCE(MAX(companyId),0)
        FROM Company
        """,
        )[0]
        + 1
    )

    records = []

    company_names = {
        row[0] for row in fetch_all(connection, "SELECT companyName FROM Company")
    }
    for i in range(count):
        base_name = fake.company()
        company_name = base_name
        suffix = 1
        while company_name in company_names:
            company_name = f"{base_name} ({suffix})"
            suffix += 1
        company_names.add(company_name)
        records.append((start_id + i, company_name, random.choice(sectors)))

    query = """
        INSERT INTO Company(
            companyId,
            companyName,
            sector
        )
        VALUES(%s, %s, %s)
        """
    inserted = insert_data(connection, query, records)

    print(f"Company: {inserted} records inserted")

    return [row[0] for row in fetch_all(connection, "SELECT companyId FROM Company")]


def generate_users(connection, roles, count=1000):

    records = []

    for i in range(1, count + 1):
        email = f"user{i}@example.com"

        balance = Decimal(random.randint(1000, 1000000))

        created_at = fake.date_time_between(start_date="-3y", end_date="now")

        role = random.choices(roles, weights=[1, 90, 9], k=1)[0]

        records.append(
            (
                email,
                "SYNTHETIC_PASSWORD_HASH",
                balance,
                created_at,
                role,
                created_at.date(),
            )
        )

    query = """
            INSERT INTO Users(
                email,
                passwordHash,
                balance,
                createdAt,
                roleName,
                assignedDate
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """

    inserted = insert_data(connection, query, records)
    print(f"Users: {inserted} records inserted")

    return [row[0] for row in fetch_all(connection, "SELECT email FROM Users")]


def generate_stocks(connection, company_ids, count=100):
    exchanges = ["NASDAQ", "NYSE", "TSX"]

    records = []

    for i in range(1, count + 1):
        ticker = f"STK{i:04d}"

        records.append((ticker, random.choice(company_ids), random.choice(exchanges)))

    query = """
                INSERT INTO Stocks(
                    tickerSymbol,
                    companyId,
                    exchange
                )
                VALUES(%s, %s, %s)
                ON CONFLICT (tickerSymbol) DO NOTHING
            """

    inserted = insert_data(connection, query, records)
    print(f"Stocks: {inserted} records inserted")

    return [row[0] for row in fetch_all(connection, "SELECT tickerSymbol FROM Stocks")]


def generate_stock_prices(connection, tickers, days=250):
    records = []

    start_date = date(2025, 1, 1)

    for ticker in tickers:
        price = Decimal(random.randint(20, 500))

        trading_date = start_date
        generated_days = 0

        while generated_days < days:
            if trading_date.weekday() < 5:
                opening_price = price

                change = Decimal(str(random.uniform(-0.05, 0.05)))

                closing_price = opening_price * (1 + change)

                daily_max = max(
                    opening_price,
                    closing_price,
                ) * Decimal(str(random.uniform(1, 1.03)))

                daily_min = min(opening_price, closing_price) * Decimal(
                    str(random.uniform(0.97, 1))
                )

                records.append(
                    (
                        ticker,
                        trading_date,
                        round(opening_price, 4),
                        round(closing_price, 4),
                        round(daily_max, 4),
                        round(daily_min, 4),
                    )
                )

                price = closing_price
                generated_days += 1

            trading_date += timedelta(days=1)

    query = """
        INSERT INTO StockPrices(
            tickerSymbol,
            tradingDate,
            openingPrice,
            closingPrice,
            dailyMax,
            dailyMin
        )

        VALUES(%s, %s, %s, %s,%s,%s)
        ON CONFLICT (tickerSymbol, tradingDate)
        DO NOTHING
    """

    inserted = insert_data(connection, query, records)

    print(f"StockPrices: {inserted} records inserted")


def generate_revenue_reports(connection, company_ids):

    records = []

    revenue_id = (
        fetch_one(
            connection,
            """
        SELECT COALESCE(MAX(revenueId),0)
        FROM AnnualRevenueReport
""",
        )[0]
        + 1
    )

    for company_id in company_ids:
        revenue = Decimal(random.randint(1_000_000, 10_000_000_000))

        for year in range(2016, 2026):
            growth = Decimal(str(random.uniform(-0.15, 0.25)))

            revenue = round(revenue * (1 + growth), 2)

            records.append((revenue_id, company_id, year, revenue, "USD"))

            revenue_id += 1

    query = """
        INSERT INTO AnnualRevenueReport(
            revenueId,
            companyId,
            fiscalYear,
            totalRevenue,
            currency
        )
        VALUES(%s, %s, %s, %s, %s)
        ON CONFLICT (companyId, fiscalYear)
        DO NOTHING
        """

    inserted = insert_data(connection, query, records)

    print(f"AnnualRevenueReport: {inserted} records inserted")
