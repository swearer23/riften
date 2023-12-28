import os
import json
from hunter.account import BNAccount
from hunter.models.SymbolList import SymbolList

if not os.path.exists('.holdings.json'):
  open('.holdings.json', 'w').write('[]')

class Holding:
  @staticmethod
  def init_holdings(
    account: BNAccount,
    symbol_list: SymbolList
  ):
    holdings = account.find_my_holding(
      symbol_list.get_all_symbol_as_str()
    )
    from pprint import pprint
    pprint([x for x in holdings if x['symbol'] == 'NEOUSDT'])
    holdings.sort(key=lambda x: x['time'])
    holdings = [x for x in holdings if x['isBuyer']]
    json.dump(holdings, open('.holdings.json', 'w'))

  @staticmethod
  def get_all_active_holding() -> list:
    return json.load(open('.holdings.json', 'r'))
  
  @staticmethod
  def get_active_holding_by_id(order_id):
    holdings = Holding.get_all_active_holding()
    return next(x for x in holdings if x['id'] == order_id)
  
  @staticmethod
  def get_active_holding_len():
    return len(Holding.get_all_active_holding())
  
  @staticmethod
  def remove_active_holding(order_id):
    holdings = Holding.get_all_active_holding()
    holdings = [x for x in holdings if x['id'] != order_id]
    json.dump(holdings, open('.holdings.json', 'w'))

  @staticmethod
  def concat_active_holding(trades):
    holdings = Holding.get_all_active_holding()
    new_trade = {}
    for trade in trades:
      prev_cost = new_trade.get('qty', 0) * new_trade.get('price', 0)
      curr_cost = float(trade['qty']) * float(trade['price'])
      total_qty = float(trade['qty']) + new_trade.get('qty', 0)
      curr_price = (prev_cost + curr_cost) / total_qty
      new_trade = {
        'id': trade['orderId'],
        'symbol': trade['symbol'],
        'time': trade['time'],
        'qty': float(trade['qty']) + new_trade.get('qty', 0),
        'price': curr_price,
        'interval': os.environ.get('INTERVAL')
      }
    holdings.append(new_trade)
    json.dump(holdings, open('.holdings.json', 'w'))