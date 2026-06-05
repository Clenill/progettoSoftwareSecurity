
from os import getenv
from json import load
from web3 import Web3

# database
DB_USERNAME = getenv("DB_USERNAME", "")
DB_PASSWORD = getenv("DB_PASSWORD", "")
DB_NAME = getenv("DB_NAME", "")
DB_HOST = getenv("DB_HOST", "")
DB_PORT = getenv("DB_PORT", "5432")

# api
APP_PORT = getenv("APP_PORT", "8000")
ALGORITHM = getenv("ALGORITHM", "")
SECRET_KEY = getenv("SECRET_KEY", "")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# web3
RPC_PROVIDER_URL = getenv("RPC_PROVIDER_URL", "")
w3 = Web3(Web3.HTTPProvider(RPC_PROVIDER_URL))
if not w3.is_connected():
    raise RuntimeError("Cannot connect to Web3 RPC provider")

CONTRACT_ADDRESS = w3.to_checksum_address(getenv("CONTRACT_ADDRESS", ""))
with open(getenv("CONTRACT_ABI", "")) as f:
    CONTRACT_ABI = load(f)["abi"]

CONTRACT = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
PRIVATE_KEY = getenv("PRIVATE_KEY", "")
W3_ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)

#SCALE = 10**8;
SCALE = int(getenv("SCALE", str(10**8)))

