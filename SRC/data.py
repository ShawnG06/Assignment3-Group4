import random
import uuid

from datetime import date, datetime, timedelta
from decimal import Decimal
from faker import Faker

from database import insert_data, fetch_all, fetch_one

fake = Faker()

random.seed(42)
Faker.seed(42)


def generate_roles(connection):
    records = [("Admin",), ("Trader",), ("Analyst",)]

    query = """

        INSSERT INTO Roles(roleName)
        VALUES(%s)
        ON CONFLICT (roleName) DO NOthing
    """

    count = insert_data(connection, query, records)

    print(f"Roles: {count} records inserted")

    return [record[0] for record in records]


def generate_companies(connection, count=80):
    sectors = [
        "Technology",
        "Healthcare",
        "EnergyFinanceIndustrialsCommunicationArt History?",
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

    for i in range(count):
        records.append((start_id + i, fake.company(), random.choice(sectors)))

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
