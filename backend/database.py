import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.SUPABASE_DB_HOST,
            port=Config.SUPABASE_DB_PORT,
            database=Config.SUPABASE_DB_NAME,
            user=Config.SUPABASE_DB_USER,
            password=Config.SUPABASE_DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def execute_query(query, params=None, fetch=True):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            conn.commit()
            return result
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
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        conn.commit()
        
        if cursor.description:
            result = cursor.fetchone()
            return result
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
