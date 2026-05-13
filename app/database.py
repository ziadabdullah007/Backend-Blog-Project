import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLSERVER_HOST = os.getenv("DB_HOST", "SANDY")
SQLSERVER_NAME = os.getenv("DB_NAME", "blog_db")
SQLSERVER_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

DEFAULT_SQLSERVER_URL = (
    "mssql+pyodbc:///?odbc_connect="
    + quote_plus(
        f"DRIVER={{{SQLSERVER_DRIVER}}};"
        f"SERVER={SQLSERVER_HOST};"
        f"DATABASE={SQLSERVER_NAME};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
)

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLSERVER_URL)

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()