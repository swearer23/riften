class Holdings(list):
  def last(self):
    if self.is_empty():
      return None
    return self[-1]
  
  def is_empty(self):
    open_trades = [trade for trade in self if trade.is_active()]
    return len(open_trades) == 0