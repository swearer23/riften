import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_SECRET_KEY')

