# db.py
import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")  # 6543 for Supabase pooler; use 5432 for direct
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_SSL  = os.getenv("DB_SSL", "require")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode={DB_SSL}"
)

# Create connection pool (no 'open' kw)
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
)

# Optional: warm the pool at import-time (or in app startup)
# pool.wait()

def test_connection():
    # Borrow a conn from pool and run a simple query
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT NOW()")
            return cur.fetchone()[0]
# db.py (append these)

def query_rows(sql: str, params: tuple = ()):
    """
    Run a SELECT and return list of dicts. Easier to JSON-ify.
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [c.name for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

def query_value(sql: str, params: tuple = (), default=None):
    """
    Run a SELECT that returns a single value (first row, first column).
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            r = cur.fetchone()
            return r[0] if r and r[0] is not None else default
