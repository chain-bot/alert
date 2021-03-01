import firebase_admin
from dotenv import load_dotenv
import os

from firebase_admin import credentials, firestore

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
HEADERS = {
    "Authorization": "Bot " + TOKEN,
    "X-MBX-APIKEY": BINANCE_API_KEY
}
APPLICATION_ID = os.getenv('APPLICATION_ID')
DEBUG_GUILD_ID = os.getenv('DEBUG_GUILD_ID')
DISCORD_API_BASE_URL = f'https://discord.com/api/v8/applications'
# Create service account JSON file
FIRESTORE_JSON = os.getenv('firestoreAdmin')
PRINT_LINE = '---------------------------------------------------------------'
BINANCE_BASE_URL = 'https://api.binance.com/api/v3'

if FIRESTORE_JSON is None:
    print("WARNING: local use")
else:
    with open("firestore-admin.json", "w") as jsonFile:
        jsonFile.write(FIRESTORE_JSON)

cred = credentials.Certificate('firestore-admin.json')
firebase_admin.initialize_app(cred)
FIRESTORE_CLIENT = firestore.client()
