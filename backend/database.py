import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
from datetime import datetime, date, time


def get_db_connection():
  try:
    conn = psycopg2.connect(host=Config.SUPABASE_DB_HOST,
                            port=Config.SUPABASE_DB_PORT,
                            database=Config.SUPABASE_DB_NAME,
                            user=Config.SUPABASE_DB_USER,
                            password=Config.SUPABASE_DB_PASSWORD)
    return conn
  except Exception as e:
    print(f"Database connection error: {e}")
    raise


def serialize_value(value):
  """Convert datetime/date/time objects to ISO format strings"""
  if isinstance(value, datetime):
    # Return as ISO format: YYYY-MM-DDTHH:MM:SS
    return value.strftime('%Y-%m-%dT%H:%M:%S')
  elif isinstance(value, date):
    # Return as: YYYY-MM-DD
    return value.strftime('%Y-%m-%d')
  elif isinstance(value, time):
    # Return as: HH:MM:SS
    return value.strftime('%H:%M:%S')
  else:
    return value


def serialize_row(row):
  """Convert a database row to a serialized dictionary"""
  if not row:
    return None

  return {key: serialize_value(value) for key, value in row.items()}


def execute_query(query, params=None, fetch=True):
  """
    Execute a database query with datetime serialization.

    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch: Whether to fetch results

    Returns:
        List of serialized rows if fetch=True, otherwise row count
    """
  conn = None
  cursor = None
  try:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or ())

    if fetch:
      result = cursor.fetchall()
      conn.commit()
      # Serialize all rows
      return [serialize_row(dict(row)) for row in result]
    else:
      conn.commit()
      return cursor.rowcount

  except Exception as e:
    if conn:
      conn.rollback()
    raise e
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()


def execute_insert(query, params=None):
  """
    Execute an INSERT query and return the inserted row with serialization.

    Args:
        query: SQL INSERT query with RETURNING clause
        params: Query parameters tuple

    Returns:
        Serialized dict of the inserted row
    """
  conn = None
  cursor = None
  try:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or ())
    conn.commit()

    if cursor.description:
      result = cursor.fetchone()
      # Serialize the result
      return serialize_row(dict(result)) if result else None
    return None

  except Exception as e:
    if conn:
      conn.rollback()
    raise e
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()
