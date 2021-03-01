import firebase_admin
import os
from firebase_admin import credentials, firestore

FIRESTORE_JSON = os.getenv('FIRESTORE_ADMIN')
if FIRESTORE_JSON is None:
    print("WARNING: local use")
else:
    with open("firestore-admin.json", "w") as jsonFile:
        jsonFile.write(FIRESTORE_JSON)

cred = credentials.Certificate('firestore-admin.json')
firebase_admin.initialize_app(cred)
FIRESTORE_CLIENT = firestore.client()


def get_ath_data(exchange: str):
    doc_ref = FIRESTORE_CLIENT.collection('ATH').document(exchange)
    return doc_ref.get().to_dict()


def set_exchange_ath_data(exchange: str, base: str, quote: str, ath: float):
    doc_ref = FIRESTORE_CLIENT.collection('ATH').document(exchange)
    doc_ref.set({base: {quote: ath}}, merge=True)


if __name__ == "__main__":
    from dotenv import load_dotenv
    import json

    load_dotenv(dotenv_path='../../.env')
    TEST_EXCHANGE = 'TEST_EXCHANGE'
    ath_data = get_ath_data(TEST_EXCHANGE)
    print(json.dumps(ath_data, indent=2))
    set_exchange_ath_data(TEST_EXCHANGE, 'BTC', 'USDT', 1)
    set_exchange_ath_data(TEST_EXCHANGE, 'ETH', 'BTC', 1)
