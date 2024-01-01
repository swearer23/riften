import os
from time import sleep
from enum import Enum
from datetime import datetime
from binance.client import Client
from hunter.bnclient import BNClient
from common import beginning_of_interval
from strats.utils import downcross
from hunter.prepare_data import fetch_data
from hunter.models.Holding import Holding
from hunter.logger import LoggerMixin

class PositionCloseReason(Enum):
  STOP_LOSS_PERC = 'STOP_LOSS_PERC'
  STOP_LOSS_RSI = 'STOP_LOSS_RSI'
  TAKE_PROFIT = 'TAKE_PROFIT'
  MANUAL = 'MANUAL'

class Position(LoggerMixin):
  def __init__(self, **kwargs):
    self.bnclient = BNClient()
    self.__raw__ = kwargs
    self.id = kwargs.get('id')
    self.symbol = kwargs.get('symbol')
    self.price = float(kwargs.get('price'))
    self.quantity = kwargs.get('qty')
    self.time = kwargs.get('time')
    self.interval = kwargs.get('interval', '5m')
    self.closing_reason = False

  def try_to_close(self):
    end = beginning_of_interval(datetime.now(), self.interval)
    df, _ = fetch_data((self.symbol, self.interval, end))
    self.closing_reason = self.is_closing_for(df)
    if self.closing_reason:
      trades = self.close()
      self.post_close(trades)
      return True
    else:
      current_price = df['close'].values.tolist()[-1]
      current_rsi_14 = df['rsi_14'].values.tolist()[-1]
      self.holding_report_logger(
        symbol=self.symbol,
        price=self.price,
        quantity=self.quantity,
        current_price=current_price,
        current_rsi_14=current_rsi_14)
      return False

  def close(self):
    order = self.bnclient.client.create_order(
        symbol=self.symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=self.quantity
    )
    while True:
      bnorder = self.bnclient.client.get_order(
        symbol=self.symbol,
        orderId=order.get('orderId')
      )
      if bnorder.get('status') == 'FILLED':
        trades = self.bnclient.client.get_my_trades(symbol=self.symbol, orderId=order.get('orderId'))
        return trades
      else:
        print('waiting for order to be filled', bnorder.get('status'))
        sleep(1)
  
  def calculate_profit(self, closed_trades):
    total_selling_amount = sum([
      float(x['price']) * float(x['qty'])
      for x in closed_trades
    ])
    total_buying_amount = float(self.price) * float(self.quantity)
    return (total_selling_amount - total_buying_amount) / total_buying_amount * 100
  
  def is_closing_for(self, df):
    take_profit_downcross_rsi = int(os.environ.get('TAKE_PROFIT_DOWNCROSS_RSI'))
    stop_loss_downcross_rsi = int(os.environ.get('STOP_LOSS_DOWNCROSS_RSI'))
    stop_loss_percentage = float(os.environ.get('STOP_LOSS_PERCENTAGE'))
    df[f'downcross_{stop_loss_downcross_rsi}'] = downcross(df, 'rsi_14', stop_loss_downcross_rsi)
    df[f'downcross_{take_profit_downcross_rsi}'] = downcross(df, 'rsi_14', take_profit_downcross_rsi)
    current_price = df['close'].values.tolist()[-1]
    stoploss = current_price < self.price * (1 - stop_loss_percentage)
    if df[f'downcross_{stop_loss_downcross_rsi}'].iloc[-1]:
      return PositionCloseReason.STOP_LOSS_RSI
    elif df[f'downcross_{take_profit_downcross_rsi}'].iloc[-1]:
      return PositionCloseReason.TAKE_PROFIT
    # elif stoploss:
    #   return PositionCloseReason.STOP_LOSS_PERC
    else:
      return False
  
  def post_close(self, trades):
    Holding.remove_active_holding(self.id)
    profit = self.calculate_profit(trades)
    self.trade_summary_logger({
      'profit': profit,
      'closing_reason': self.closing_reason.value,
      'open_time': datetime.fromtimestamp(self.time/1000).strftime('%Y-%m-%d %H:%M:%S'),
      'close_time': datetime.fromtimestamp(trades[0]['time']/1000).strftime('%Y-%m-%d %H:%M:%S'),
      **self.__raw__
    }, trades)
  
  def __dict__(self):
    return self.__raw__