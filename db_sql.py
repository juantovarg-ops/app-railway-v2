import os
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DATABASE_URL"))


def init_sql():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id        SERIAL PRIMARY KEY,
                query     TEXT NOT NULL,
                n_results INTEGER DEFAULT 0,
                ts        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


def log_search(query: str, n_results: int):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO search_logs (query, n_results) VALUES (:q, :n)"),
            {"q": query, "n": n_results},
        )
        conn.commit()


def get_search_stats():
    """Returns list of (label, value) tuples for the sidebar."""
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM search_logs")).scalar()
        today = conn.execute(
            text("SELECT COUNT(*) FROM search_logs WHERE ts::date = CURRENT_DATE")
        ).scalar()
        top = conn.execute(
            text("""
                SELECT query FROM search_logs
                GROUP BY query ORDER BY COUNT(*) DESC LIMIT 1
            """)
        ).scalar()
    return [
        ("Total búsquedas", total or 0),
        ("Búsquedas hoy", today or 0),
        ("Query más popular", top or "—"),
    ]
