# Optional SQLite persistence (not used by default for simplicity)
from sqlalchemy import create_engine, text
from .schema_sql import SCHEMA_SQL
from ..config import get_settings

def init_db():
    settings = get_settings()
    engine = create_engine(f"sqlite:///{settings.SQLITE_PATH}", future=True)
    with engine.begin() as conn:
        conn.exec_driver_sql(SCHEMA_SQL)
    return engine
