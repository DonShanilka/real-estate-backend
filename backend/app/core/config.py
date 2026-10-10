from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MYSQL_SERVER_URL = os.getenv("MYSQL_SERVER_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "real_estate_db")
DATABASE_URL = os.getenv("DATABASE_URL") or f"{MYSQL_SERVER_URL}/{DATABASE_NAME}"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "600"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or None

B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
