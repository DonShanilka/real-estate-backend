from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError


MYSQL_SERVER_URL = "mysql+pymysql://root:Shanilka800%40%23@localhost:3306"

DATABASE_NAME = "real_estate_db"

DATABASE_URL = f"{MYSQL_SERVER_URL}/{DATABASE_NAME}"

# CREATE DATABASE IF NOT EXISTS

server_engine = create_engine(MYSQL_SERVER_URL)

with server_engine.connect() as conn:
    conn.execute(
        text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    )
    conn.commit()

# MAIN DATABASE ENGINE
engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# DATABASE DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()