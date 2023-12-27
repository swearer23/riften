import sys
import json
from datetime import datetime
from multiprocessing import Pool, cpu_count
from common import beginning_of_interval
from hunter.prepare_data import fetch_data, get_active_symbols
from hunter.trade import BinaceTradingBot
from hunter.account import BNAccount
from hunter.models.SymbolList import SymbolList
from utils import load_config, Tasks
load_config()

bot = BinaceTradingBot()
account = BNAccount()
symbolList = SymbolList()

def parse_args():
  if len(args) > 1:
    if args[1] == 'init':
      return Tasks.INIT_HOLDING, None
    else:
      interval = args[1]
      return Tasks.SCAN_SYMBOL, interval
  else:
    raise Exception('interval is required')
  
def init_holding():
  holdings = account.find_my_holding(symbolList.get_all_symbol_as_str())
  holdings.sort(key=lambda x: x['time'])
  holdings = [x for x in holdings if x['isBuyer']]
  json.dump(holdings, open('.holdings.json', 'w'))

def scan_interesting_symbol(interval):
  # now = datetime(2023, 12, 26, 18, 40)
  now = datetime.now()
  end = beginning_of_interval(now, interval)
  all_symbols = symbolList.get_all_symbols()
  step = cpu_count()
  for idx in range(0, len(all_symbols), step):
    result = Pool(cpu_count()).map(
      fetch_data,
      [
        (symbol, interval, end)
        for symbol in all_symbols[idx:idx+step]
      ]
    )
    active_symbols = get_active_symbols(result)
    if len(active_symbols) > 0:
      balance = account.get_balance()
      quantity = (balance / active_symbols[0].price)
      bot.open_trade(active_symbols[0], quantity=quantity)
      break
    else:
      print('no active symbols in batch')
  pass

if __name__ == '__main__':
  args = sys.argv
  task, interval = parse_args()
  if task == Tasks.INIT_HOLDING:
    init_holding()
  elif task == Tasks.SCAN_SYMBOL:
    scan_interesting_symbol(interval)
  
