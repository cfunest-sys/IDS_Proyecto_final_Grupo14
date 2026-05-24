import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mundial")
DB_NAME = os.getenv("DB_NAME", "data_base")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-key-insegura")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400)))
