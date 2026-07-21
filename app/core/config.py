
from os import getenv
from os.path import join
from json import load
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from dotenv import load_dotenv
from string import ascii_letters, digits
from secrets import choice

load_dotenv()

# Variabili d'ambiente
LOG_PATH = getenv("LOG_PATH", "./logs")
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
ISOLATION_LEVEL = getenv("ISOLATION_LEVEL")

# web3
RPC_URL = getenv("RPC_URL", "")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, name="extradata_to_poa", layer=0)
if not w3.is_connected():
    raise RuntimeError("Cannot connect to Web3 RPC provider")

DEPLOYMENTS_PATH = getenv("DEPLOYMENTS_PATH", ".")
ARTIFACTS_PATH = getenv("ARTIFACTS_PATH", ".")
CONTRACT_NAME = getenv("CONTRACT_NAME", "contract")

with open(join(ARTIFACTS_PATH, "contracts", f"{CONTRACT_NAME}.sol", f"{CONTRACT_NAME}.json")) as f:
    CONTRACT_ABI = load(f)["abi"]
with open(join(DEPLOYMENTS_PATH, "deployed_addresses.json")) as f:
    CONTRACT_ADDRESS = load(f)[f"{CONTRACT_NAME}Module#{CONTRACT_NAME}"]

CONTRACT = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
PRIVATE_KEY = getenv("PRIVATE_KEY", "")
W3_ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)

SCALE = int(getenv("SCALE", str(10**8)))

