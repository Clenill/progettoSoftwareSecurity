
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

