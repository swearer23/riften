import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
from common import get_all_symbols, beginning_of_interval, banned_symbols
from hunter.prepare_data import fetch_data, filter_active_symbols
from hunter.trade import BinaceTradingBot

bot = BinaceTradingBot(is_test=True)

if __name__ == '__main__':
  print(bot.find_holding_trading())
  exit()
  args = sys.argv
  now = datetime.now()
  if len(args) > 1:
    interval = args[1]
  else:
    interval = '5m'
  end = beginning_of_interval(now, interval)
  all_symbols = [x for x in get_all_symbols() if x not in banned_symbols]
  step = cpu_count()
  for idx in range(0, len(all_symbols), step):
    result = Pool(cpu_count()).map(
      fetch_data,
      [
        (symbol, interval, now)
        for symbol in all_symbols[idx:idx+step]
      ]
    )
    active_symbols = filter_active_symbols(result) 
    if len(active_symbols) > 0:
      bot.open_trade(active_symbols[0])
      break
    else:
      print('no active symbols in batch')
