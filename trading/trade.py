class Trade:
  def __init__(self, price, dt) -> None:
    self.buy_price = price
    self.buy_dt = dt
    self.sell_price = 0
    self.sell_dt = None
    self.closed = False
    self.profit = 0

  def close(self, price, dt):
    self.sell_price = price
    self.sell_dt = dt
    self.closed = True
    self.profit = self.sell_price - self.buy_price

  def is_active(self):
    return self.closed == False
  
  def __repr__(self) -> str:
    return self.to_dict().__repr__()
  
  def to_dict(self):
    return {
      'buy_price': self.buy_price,
      'buy_dt': self.buy_dt,
      'sell_price': self.sell_price,
      'sell_dt': self.sell_dt,
      'profit': self.profit,
    }
