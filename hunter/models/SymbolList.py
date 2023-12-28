import os
from binance.spot import Spot
from hunter.models.Symbol import Symbol
from common import banned_symbols

class SymbolList:
  def __init__(self, quote_assets=['USDT']) -> None:
    self.raw_symbols_data = None
    self.quote_assets = None
    self.symbol_list = None
    self.filtered_symbol_list = None
    self.__map = {}
    self.__init_raw_data()
    self.__filter_banned_symbols()
    self.__init_quote_assets()
    self.__init_all_symbol()
    self.__filter_by_quote_asset(quote_assets)
    self.__transform_to_dict()
  
  def __init_raw_data(self):
    permissions = os.environ.get('TRADE_PERMISSION').split(',')
    client = Spot()
    self.raw_symbols_data = client.exchange_info(permissions=permissions).get('symbols')

  def __filter_banned_symbols(self):
    self.raw_symbols_data = [
      x for x in self.raw_symbols_data
      if x.get('symbol') not in banned_symbols
    ]
  
  def __init_quote_assets(self):
    quote_assets = [
      item['quoteAsset'] for item in
      self.raw_symbols_data
    ]
    self.quote_assets = list(set(quote_assets))

  def __init_all_symbol(self):
    self.symbol_list = [
      Symbol(**item)
      for item in self.raw_symbols_data
    ]

  def __filter_by_quote_asset(self, quote_assets):
    self.symbol_list = [
      symbol for symbol in self.symbol_list
      if symbol.quoteAsset in quote_assets
    ]

  def __transform_to_dict(self):
    for symbol in self.symbol_list:
      self.__map[symbol.symbol] = symbol
  
  def get_all_symbol_as_str(self):
    return [symbol.symbol for symbol in self.symbol_list]
  
  def get_all_symbols(self):
    return self.symbol_list
  
  def find_by_base_asset(self, base_asset):
    return self.__map.get(f'{base_asset}USDT')
  
  def find_by_symbol_name(self, symbol_name):
    return self.__map.get(symbol_name)
  