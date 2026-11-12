"""Create the schema, load sample data and set demo passwords.

Usage:  python init_db.py          (DROPS and recreates all project tables)
"""
import pathlib

import oracledb
from werkzeug.security import generate_password_hash

from config import Config

BASE = pathlib.Path(__file__).parent / "database"
TABLES = ["support_ticket", "review", "delivery", "payment", "order_item", "orders",
          "food_item", "category", "restaurant", "customer", "admin_user"]


def run_script(cur, path):
    for stmt in path.read_text(encoding="utf-8").split(";"):
        sql = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()
        if sql:
            cur.execute(sql)


def main():
    conn = oracledb.connect(user=Config.ORACLE_USER, password=Config.ORACLE_PASSWORD,
                            dsn=Config.ORACLE_DSN)
    cur = conn.cursor()
    for t in TABLES:
        try:
            cur.execute(f"DROP TABLE {t} CASCADE CONSTRAINTS PURGE")
        except oracledb.DatabaseError:
            pass  # table did not exist
    run_script(cur, BASE / "schema.sql")
    run_script(cur, BASE / "seed.sql")
    cur.execute("UPDATE customer SET password_hash = :h WHERE password_hash = 'PENDING'",
                {"h": generate_password_hash("password123")})
    cur.execute("INSERT INTO admin_user (username, password_hash) VALUES (:u, :h)",
                {"u": "admin", "h": generate_password_hash("admin123")})
    conn.commit()
    conn.close()
    print("Database ready. Customer login: ali@example.com / password123 | Admin: admin / admin123")


if __name__ == "__main__":
    main()
