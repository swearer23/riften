import os
import math
from binance.client import Client
from utils import load_config

load_config()

class BinaceTradingBot:
  def __init__(self, is_test=True):
    self.is_test = is_test
    self.client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'), testnet=is_test)

  def get_account_balance(self):
    if self.is_test:
      return 10000
    else:
      account = self.client.get_account()
      return account

  def open_trade(self, active_symbol, is_test=True):
    symbol = active_symbol[0]
    order_side = Client.SIDE_BUY
    order_type = Client.ORDER_TYPE_MARKET
    quantity = math.floor(self.get_account_balance() / float(active_symbol[-1]))
    print('open trade', active_symbol, quantity)
    self.client.create_test_order(
      symbol=symbol,
      side=order_side,
      type=order_type,
      quantity=quantity,
      computeCommissionRates='true'
    )

  def find_holding_trading(self):
    return self.client.get_all_orders()
