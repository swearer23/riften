import os
from binance.client import Client

class BNClient:
  _instance = None
  client = None
  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self):
    self.is_test = os.getenv('IS_TEST') == 'true'
    self._init_client()

  def _init_client(self):
    self.client = Client(
      os.getenv('BINANCE_API_KEY'),
      os.getenv('BINANCE_SECRET_KEY'),
      testnet=self.is_test
    )

  def is_testnet(self):
    return self.is_test
  