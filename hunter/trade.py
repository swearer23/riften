import uuid
from binance.client import Client
from binance.exceptions import BinanceAPIException
from hunter.bnclient import BNClient
from hunter.prepare_data import ActiveSymbol
from hunter.models.Position import Position
from hunter.models.Holding import Holding
from hunter.models.Order import BNOrder
from hunter.logger import LoggerMixin
from hunter.account import BNAccount

class BinaceTradingBot(LoggerMixin):
  def __init__(self, account: BNAccount):
    self.bnclient = BNClient()
    self.holdings = []
    self.account = account

  def open_trade(self, active_symbol: ActiveSymbol):
    symbol = active_symbol.symbol
    price = self.get_price_by_symbol(symbol)
    balance = self.account.get_balance(asset='USDT')
    quantity = active_symbol.trim_to_valid_quantity(balance, self.is_test())
    if quantity < 0:
      return
    self.open_trade_logger(
      symbol=symbol,
      quantity=quantity,
      price=price
    )
    try:
      order = self.create_order(
        symbol=active_symbol.symbol,
        quantity=quantity
      )
      trades = order.poll_order_status()
      if trades and len(trades) > 0:
        Holding.concat_active_holding(trades)
    except BinanceAPIException as e:
      if e.code == -2010:
        self.open_trade_failed_logger(
          symbol=symbol,
          quantity=quantity,
          cost=quantity * price,
          balance=self.account.get_balance(asset='USDT'),
          reason='INSUFFICIENT_BALANCE'
        )
      elif e.code == -1013:
        self.open_trade_failed_logger(
          symbol=symbol,
          quantity=quantity,
          cost=quantity * price,
          min_notional=active_symbol.get_min_notional(),
          balance=self.account.get_balance(asset='USDT'),
          reason='MIN_NOTIONAL'
        )
      else:
        raise e

  def create_order(self, symbol, quantity):
    order_side = Client.SIDE_BUY
    order_type = Client.ORDER_TYPE_MARKET
    order = self.bnclient.client.create_order(
      symbol=symbol,
      side=order_side,
      type=order_type,
      quantity=quantity,
      recvWindow=60000,
      newClientOrderId=str(uuid.uuid4())
    )
    order = BNOrder(**order)
    return order
  
  def get_price_by_symbol(self, symbol):
    return float(self.bnclient.client.get_symbol_ticker(symbol=symbol).get('price'))

  def is_test(self):
    return self.bnclient.is_test
  
  def set_holdings(self, holdings):
    self.holdings = [Position(**x) for x in holdings]

  def close_holdings(self) -> list[Position]:
    return [x for x in self.holdings if not x.try_to_close()]
  