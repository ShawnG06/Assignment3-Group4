import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def connect():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(ps.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
    )


def insert_data(connection, query, records):
    if not records:
        return 0

    with connection.cursor() as cursor:
        cursor.executemany(query, records)

        count = cursor.rowcount

    return count


def fetch_all(connection, query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(connection, query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()
