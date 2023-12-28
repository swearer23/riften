from time import sleep
from hunter.bnclient import BNClient
from hunter.models.Holding import Holding
from hunter.logger import LoggerMixin

class BNOrder(LoggerMixin):
  def __init__(self, **kwargs):
    self.bnclient = BNClient()
    self.symbol = kwargs.get('symbol')
    self.order_id = kwargs.get('orderId')
    self.price = kwargs.get('price')
    self.executed_qty = kwargs.get('executedQty')
    self.orig_qty = kwargs.get('origQty')

  def poll_order_status(self):
    while True:
      bnorder = self.bnclient.client.get_order(
        symbol=self.symbol,
        orderId=self.order_id
      )
      status = bnorder.get('status')
      self.polling_order_status_logger(
        symbol=self.symbol,
        order_id=self.order_id,
        status=status
      )
      if status == 'FILLED':
        trades = self.bnclient.client.get_my_trades(symbol=self.symbol, orderId=self.order_id)
        self.order_filled_logger(
          symbol=self.symbol,
          order_id=self.order_id,
        )
        return trades
      elif bnorder.get('status') == 'EXPIRED':
        self.open_trade_failed_logger(
          symbol=self.symbol,
          quanity=self.orig_qty,
          price=self.price,
          reason='EXPIRED'
        )
        return False
      else:
        print('waiting for order to be filled', bnorder.get('status'))
        sleep(1)