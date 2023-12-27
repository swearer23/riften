import json
import uuid
from binance.client import Client
from hunter.bnclient import BNClient
from hunter.prepare_data import ActiveSymbol

class BinaceTradingBot:
  def __init__(self):
    self.bnclient = BNClient()

  def open_trade(self, active_symbol: ActiveSymbol, quantity: int):
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
      recvWindow=60000,
      newClientOrderId=str(uuid.uuid4())
    )
    print(ret)

  def get_holding_trades(self):
    trades = []
    with open('.trades.json', 'w+') as f:
      trades = json.load(f)
    trades = trades.sort(key=lambda x: x['time'])
    buys = [x for x in trades if x['isBuyer']]
    sells = [x for x in trades if not x['isBuyer']]
    for buy in buys:
      for sell in sells:
        if buy['orderId'] == sell['orderId']:
          print(buy['symbol'], buy['price'], sell['price'])
          break

  def is_test(self):
    return self.bnclient.is_test
  
  def clear_dirty_data(self):
    self.bnclient.clear_dirty_data()
  