import sys, os, time
from datetime import datetime
from hunter.trade import BinaceTradingBot
from hunter.account import BNAccount
from hunter.models.SymbolList import SymbolList
from hunter.tasks import TaskImpl
from utils import load_config, Tasks, send_mail
from common import is_beginning_of_interval

def parse_args():
  if len(args) > 1:
    if args[1] == 'init':
      return Tasks.INIT_HOLDING, None
    elif args[1] == 'local':
      interval = args[2]
      return Tasks.LOCAL_SCAN_SYMBOL, interval
    elif args[1] == 'scan':
      interval = args[2]
      return Tasks.SCAN_SYMBOL, interval
  else:
    raise Exception('interval is required')

try:
  load_config()
  account = BNAccount()
  symbolList = SymbolList()
  bot = BinaceTradingBot(account=account)
  tasks = TaskImpl(account, symbolList, bot)
  if __name__ == '__main__':
    args = sys.argv
    task, param = parse_args()
    if task == Tasks.INIT_HOLDING:
      tasks.init_holding()
    elif task == Tasks.SCAN_SYMBOL:
      os.environ['INTERVAL'] = param
      tasks.new_round(param)
    elif task == Tasks.LOCAL_SCAN_SYMBOL:
      while True:
        os.environ['INTERVAL'] = param
        now = datetime.now() # - timedelta(minutes=15)
        if is_beginning_of_interval(now, param):
          print(f'[{now}] is beginning of {param}')
          tasks.new_round(param)
        time.sleep(1)
    elif task == Tasks.MANUAL_CLOSE_ORDER:
      tasks.manual_close()
except Exception as e:
  send_mail(
    title=f'[{datetime.now()}] Fatal Error',
    content=f'{e}'
  )
  raise e
