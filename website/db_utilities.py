from flask import g

def query_value(sql, params=None, default=None):
    """
    Execute a query and return a single value.
    Example: SELECT COUNT(*)
    """
    try:
        g.cursor.execute(sql, params or ())
        row = g.cursor.fetchone()
        return row[0] if row else default
    except Exception as e:
        print("DB ERROR (query_value):", e)
        return default


def query_rows(sql, params=None):
    """
    Execute a query and return a list of dict rows.
    Example: SELECT id, name FROM table
    """
    try:
        g.cursor.execute(sql, params or ())
        cols = [col[0] for col in g.cursor.description]
        return [dict(zip(cols, row)) for row in g.cursor.fetchall()]
    except Exception as e:
        print("DB ERROR (query_rows):", e)
        return []
