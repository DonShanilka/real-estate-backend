from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import DATABASE_NAME, DATABASE_URL, MYSQL_SERVER_URL

# Create the configured database if it does not already exist.
server_engine = create_engine(MYSQL_SERVER_URL)
with server_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
    conn.commit()

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_property_agent_column():
    """Add the nullable agent assignment to databases created before this feature."""
    inspector = inspect(engine)
    if "properties" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("properties")}
    if "agent_id" not in columns:
        if engine.dialect.name == "sqlite":
            statement = (
                "ALTER TABLE properties ADD COLUMN agent_id INTEGER "
                "REFERENCES users(id) ON DELETE SET NULL"
            )
        else:
            statement = (
                "ALTER TABLE properties ADD COLUMN agent_id INTEGER NULL, "
                "ADD CONSTRAINT fk_properties_agent_id_users "
                "FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE SET NULL"
            )
        with engine.begin() as connection:
            connection.execute(text(statement))

    indexes = {index["name"] for index in inspect(engine).get_indexes("properties")}
    if "ix_properties_agent_id" not in indexes:
        with engine.begin() as connection:
            connection.execute(text(
                "CREATE INDEX ix_properties_agent_id ON properties (agent_id)"
            ))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
