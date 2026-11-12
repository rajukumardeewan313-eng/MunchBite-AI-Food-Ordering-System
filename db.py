"""Oracle connectivity (python-oracledb connection pool).

Every query in the project goes through query()/execute()/transaction() and
passes user input ONLY as bind variables (dict of :name -> value).
"""
import logging
from contextlib import contextmanager

import oracledb

from config import Config
from errors import DBError, ServiceError

log = logging.getLogger(__name__)
_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(
            user=Config.ORACLE_USER, password=Config.ORACLE_PASSWORD,
            dsn=Config.ORACLE_DSN, min=1, max=5, increment=1,
        )
    return _pool


@contextmanager
def transaction():
    """Yield a cursor; commit on success, rollback on any error."""
    try:
        conn = _get_pool().acquire()
    except oracledb.Error:
        log.exception("Could not connect to Oracle")
        raise DBError("Database connection failed")
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except oracledb.IntegrityError:
        conn.rollback()
        log.exception("Integrity error")
        raise ServiceError("That change conflicts with existing data "
                           "(duplicate value or record still in use).")
    except oracledb.Error:
        conn.rollback()
        log.exception("Oracle error")
        raise DBError("Database error")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query(sql, params=None):
    """Run a SELECT and return a list of dicts with lower-case keys."""
    with transaction() as cur:
        cur.execute(sql, params or {})
        cols = [c[0].lower() for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def query_one(sql, params=None):
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    """Run INSERT/UPDATE/DELETE; returns number of affected rows."""
    with transaction() as cur:
        cur.execute(sql, params or {})
        return cur.rowcount
