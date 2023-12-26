import math
from binance.client import Client
from hunter.bnclient import BNClient
from hunter.prepare_data import ActiveSymbol
from utils import floor_float, effective_precision

class BinaceTradingBot:
  def __init__(self):
    self.bnclient = BNClient()

  def open_trade(self, active_symbol: ActiveSymbol, quantity: int):
    print(active_symbol.get_filter_by_type('LOT_SIZE'))
    symbol = active_symbol.symbol
    order_side = Client.SIDE_BUY
    order_type = Client.ORDER_TYPE_LIMIT
    quantity = active_symbol.trim_to_valid_quantity(quantity)
    print('open trade', symbol, quantity, active_symbol.baseAssetPrecision)
    ret = self.bnclient.client.create_order(
      symbol=symbol,
      side=order_side,
      type=order_type,
      price=active_symbol.price,
      quantity=quantity,
      timeInForce=Client.TIME_IN_FORCE_IOC,
      recvWindow=60000
    )
    print(ret)

  def find_holding_trading(self, all_symbols):
    orders = []
    invalid_symbols = []
    for symbol in all_symbols:
      try:
        orders += self.bnclient.client.get_all_orders(symbol=symbol)
      except Exception as e:
        if e.code == -1121: # Invalid symbol
          invalid_symbols.append(symbol)
          continue
    if len(invalid_symbols) > 0:
      print('invalid symbols')
      print(invalid_symbols)
    return orders
  
  def is_test(self):
    return self.bnclient.is_test
  