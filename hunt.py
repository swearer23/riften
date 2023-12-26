import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
from common import beginning_of_interval
from hunter.prepare_data import fetch_data, get_active_symbols
from hunter.trade import BinaceTradingBot
from hunter.account import BNAccount
from hunter.models.SymbolList import SymbolList
from utils import load_config
load_config()

bot = BinaceTradingBot()
account = BNAccount()
symbolList = SymbolList()
print(bot.find_holding_trading(symbolList.get_all_symbol_as_str()))
exit()

if __name__ == '__main__':
  args = sys.argv
  now = datetime.now()
  # now = datetime(2023, 12, 26, 18, 40)
  if len(args) > 1:
    interval = args[1]
  else:
    interval = '5m'
  end = beginning_of_interval(now, interval)
  all_symbols = symbolList.get_all_symbols()
  step = cpu_count()
  for idx in range(0, len(all_symbols), step):
    result = Pool(cpu_count()).map(
      fetch_data,
      [
        (symbol, interval, now)
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
