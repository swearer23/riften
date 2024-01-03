import os
from utils import floor_float, effective_precision
from utils.constants import buy_rsi

class Symbol:
  def __init__(self, **kwargs) -> None:
    self.symbol = kwargs['symbol']
    self.baseAsset = kwargs['baseAsset']
    self.quoteAsset = kwargs['quoteAsset']
    self.baseAssetPrecision = kwargs['baseAssetPrecision']
    self.quoteAssetPrecision = kwargs['quoteAssetPrecision']
    self.filters = kwargs['filters']
    self.__filters = None
    self.__deconstruct_filters()

  def __deconstruct_filters(self):
    if self.__filters is not None:
      return
    else:
      self.__filters = {}
      for filter in self.filters:
        self.__filters[filter['filterType']] = filter

  def get_filter_by_type(self, filter_type):
    return self.__filters[filter_type]
  
  def get_min_qyt(self):
    return float(self.get_filter_by_type('LOT_SIZE').get('minQty'))
  
  def get_min_notional(self):
    return float(self.get_filter_by_type('NOTIONAL').get('minNotional'))

class ActiveSymbol(Symbol):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.raw_df = kwargs['raw_df']
    self.interval = kwargs['interval']
    self.rsi_14 = kwargs['rsi_14']
    self.price = kwargs['price']

  def get_surge_factor(self):
    upbars = []
    downbars = []
    index = len(self.raw_df) - 1
    while True:
      if index < 0:
        break
      row = self.raw_df.iloc[index]
      if row['close'] > row['open']:
        upbars.append(row)
      else:
        downbars.append(row)
      if len(upbars) > 0 and len(downbars) > 0 and len(upbars) == len(downbars):
        break
      index -= 1
    if len(upbars) == 0 or len(downbars) == 0:
      return 0
    up_rally_volume = sum([x['volume'] for x in upbars])
    down_rally_volume = sum([x['volume'] for x in downbars])
    up_rally_price_diff = sum([x['close'] - x['open'] for x in upbars])
    down_rally_price_diff = sum([x['open'] - x['close'] for x in downbars])
    up_rally_amount = up_rally_volume * up_rally_price_diff
    down_rally_amount = down_rally_volume * down_rally_price_diff
    surge_factor = up_rally_amount / down_rally_amount if down_rally_amount > 0 else 0
    return surge_factor
  
  def get_last_upcross_buy_rsi(self):
    row = self.raw_df.iloc[-1]
    sub_df = self.raw_df[self.raw_df[f'upcross_{buy_rsi}'] == True]
    sub_df = sub_df[sub_df['open_time'] < row['open_time']]
    return (
      row['open_time'] - sub_df['open_time'].iloc[-1]
    ).total_seconds() / 60 if len(sub_df) > 0 else None

  def trim_to_valid_quantity(self, balance, is_test=False):
    quantity = balance / self.price
    if quantity < self.get_min_qyt() or balance < self.get_min_notional():
      return -1
    stepsize = self.get_filter_by_type('LOT_SIZE').get('stepSize')
    quantity_precision = effective_precision(stepsize)
    quantity_precision = min(quantity_precision, self.baseAssetPrecision)
    if is_test:
      quantity = self.get_min_qyt()
    min_notional = self.get_min_notional()
    if quantity * self.price < min_notional:
      quantity = min_notional * 1.1 / self.price
    return floor_float(quantity, quantity_precision)