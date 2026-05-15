from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:Shanilka800%40%23@localhost:3306"

# connect WITHOUT database
engine = create_engine(DATABASE_URL)

# Auto create database
with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS real_estate_db"))
    conn.commit()

# reconnect WITH database
DATABASE_URL_DB = "mysql+pymysql://root:Shanilka800%40%23@localhost:3306/real_estate_db"

engine = create_engine(DATABASE_URL_DB)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()