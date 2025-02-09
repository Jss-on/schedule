import os
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

class Database:
    _pool = None

    def __init__(self, config=None):
        if config is None:
            config = {
                "dbname": os.getenv("DB_NAME", "driving_school"),
                "user": os.getenv("DB_USER", "user"),
                "password": os.getenv("DB_PASSWORD", "password"),
                "host": os.getenv("DB_HOST", "localhost"),
                "port": os.getenv("DB_PORT", "5432")
            }
        
        if Database._pool is None:
            Database._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **config
            )

    @contextmanager
    def get_cursor(self):
        conn = self._pool.getconn()
        try:
            yield conn.cursor(cursor_factory=RealDictCursor)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def close(self):
        if self._pool is not None:
            self._pool.closeall()
            Database._pool = None
