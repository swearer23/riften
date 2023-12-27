from multiprocessing import Pool, cpu_count
from time import sleep
from hunter.bnclient import BNClient
from hunter.models.SymbolList import SymbolList

class BNAccount:
  def __init__(self) -> None:
    self.bnclient = BNClient()
    self.__invalid_symbols = []

  def get_balance(self, asset='USDT'):
    balences = self.bnclient.client.get_account()['balances']
    for item in balences:
      if item['asset'] == asset:
        return float(item['free'])
      
  def get_holding_trading(self, symbol):
    try:
      order = self.bnclient.client.get_my_trades(symbol=symbol)
      if len(order) > 0:
        order = order[0]
        return order
      else:
        return None
    except Exception as e:
      if e.code == -1121: # Invalid symbol
        self.__invalid_symbols.append(symbol)
      else:
        print(e)
      return None
  
  def find_my_holding(self, all_symbols):
    self.__invalid_symbols = []
    concurrent_count = cpu_count()
    orders = []
    for idx in range(0, len(all_symbols), concurrent_count):
      orders += Pool(concurrent_count).map(
        self.get_holding_trading,
        all_symbols[idx:idx+concurrent_count]
      )
      sleep(2)
      
    if len(self.__invalid_symbols) > 0:
      print('invalid symbols')
      print(self.__invalid_symbols)
    return [x for x in orders if x is not None]
  
  def get_all_balance(self):
    return self.bnclient.client.get_account()['balances']
  