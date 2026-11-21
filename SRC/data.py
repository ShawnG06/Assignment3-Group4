import random
import uuid
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker

from database import fetch_all, fetch_one, insert_data

fake = Faker()

random.seed(42)
Faker.seed(42)


def generate_roles(connection):
    records = [("ADMIN",), ("TRADER",)]

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

    return [
        row[0]
        for row in fetch_all(
            connection, "SELECT companyId FROM Company ORDER BY companyId"
        )
    ]


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

    return [
        row[0] for row in fetch_all(connection, "SELECT email FROM Users ORDER BY email")
    ]


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

    return [
        row[0]
        for row in fetch_all(
            connection, "SELECT tickerSymbol FROM Stocks ORDER BY tickerSymbol"
        )
    ]


def generate_holdings(connection, user_emails, tickers, count=5000):
    if not user_emails or not tickers:
        print("Holdings: skipped because users or stocks are missing")
        return 0

    possible_pairs = len(user_emails) * len(tickers)
    selected_pairs = random.sample(range(possible_pairs), k=min(count, possible_pairs))

    records = []
    for pair_number in selected_pairs:
        user_index, ticker_index = divmod(pair_number, len(tickers))
        ticker = tickers[ticker_index]
        quantity = Decimal(random.randint(1, 100000)) / Decimal("1000")
        average_price = Decimal(random.randint(1000, 500000)) / Decimal("100")
        records.append(
            (
                user_emails[user_index],
                ticker,
                f"{ticker} position",
                quantity,
                average_price,
            )
        )

    query = """
        INSERT INTO Holdings(email, tickerSymbol, holdingName, quantity, averagePrice)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (email, tickerSymbol) DO NOTHING
    """
    inserted = insert_data(connection, query, records)
    print(f"Holdings: {inserted} records inserted")
    return inserted


def generate_transactions(connection, user_emails, tickers, count=5000):
    if not user_emails or not tickers:
        print("Transactions: skipped because users or stocks are missing")
        return 0

    namespace = uuid.UUID("d66dd17e-87cf-5d54-b2d6-566a98f3f8e9")
    records = []
    for number in range(1, count + 1):
        email = random.choice(user_emails)
        ticker = random.choice(tickers)
        transaction_id = uuid.uuid5(namespace, f"transaction-{number}-{email}-{ticker}")
        quantity = Decimal(random.randint(1, 100000)) / Decimal("1000")
        price = Decimal(random.randint(1000, 500000)) / Decimal("100")
        created_at = fake.date_time_between(start_date="-3y", end_date="now")
        transaction_type = random.choice(("BUY", "SELL"))
        records.append(
            (
                transaction_id,
                email,
                ticker,
                quantity,
                created_at,
                transaction_type,
                price,
            )
        )

    query = """
        INSERT INTO Transactions(
            id, email, tickerSymbol, quantity, createdAt, transactionType, price
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    inserted = insert_data(connection, query, records)
    print(f"Transactions: {inserted} records inserted")
    return inserted


def generate_ai_analyses(connection, tickers, count=500):
    if not tickers:
        print("AIAnalyses: skipped because stocks are missing")
        return 0

    namespace = uuid.UUID("a99c886e-e478-54c0-87b0-3e98fbaf7d73")
    recommendations = ("BUY", "SELL", "HOLD")
    records = []
    for number in range(1, count + 1):
        ticker = tickers[(number - 1) % len(tickers)]
        analysis_id = uuid.uuid5(namespace, f"analysis-{number}-{ticker}")
        predicted_price = Decimal(random.randint(1000, 500000)) / Decimal("100")
        model_accuracy = Decimal(random.randint(5000, 10000)) / Decimal("10000")
        prediction_time = fake.date_time_between(start_date="-2y", end_date="now")
        records.append(
            (
                analysis_id,
                ticker,
                prediction_time,
                predicted_price,
                random.choice(recommendations),
                model_accuracy,
                f"Synthetic demonstration analysis for {ticker}.",
            )
        )

    query = """
        INSERT INTO AIAnalyses(
            analysisUUID, tickerSymbol, predictionTimestamp, predictedPrice,
            recommendation, modelAccuracy, reasoning
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (analysisUUID) DO NOTHING
    """
    inserted = insert_data(connection, query, records)
    print(f"AIAnalyses: {inserted} records inserted")
    return inserted


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
