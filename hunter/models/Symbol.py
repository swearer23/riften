from utils import floor_float, effective_precision

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
    self.interval = kwargs['interval']
    self.rsi_14 = kwargs['rsi_14']
    self.price = kwargs['price']

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