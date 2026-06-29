
from os import getenv
from dotenv import load_dotenv
from string import ascii_letters, digits
from secrets import choice

load_dotenv()

# Variabili d'ambiente
DB_USERNAME = getenv("DB_USERNAME", "username")
DB_PASSWORD = getenv("DB_PASSWORD", "password")
DB_NAME = getenv("DB_NAME", "database")
DB_PORT = getenv("DB_PORT", "5432")
DB_HOST = getenv("DB_HOST", "localhost")
APP_PORT = getenv("APP_PORT", "8000")
SECRET_KEY = getenv("SECRET_KEY", ''.join(
    # Se non presente, genera una chiave casuale
    [choice(ascii_letters + digits) for x in range(20)]
))
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "5"))
MAX_REQUESTS = int(getenv("MAX_REQUESTS", "10"))
CLEANUP_INTERVAL_SECONDS = int(getenv("CLEANUP_INTERVAL", "10"))
MAX_LOG_FILE_SIZE = getenv("MAX_LOG_FILE_SIZE", "10 MB")
LOG_RETENTION = getenv("LOG_RETENTION", "30 days")

