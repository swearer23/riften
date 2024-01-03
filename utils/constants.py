from utils import load_config
config = load_config()
import os

from enum import Enum

class Tasks(Enum):
  INIT_HOLDING = 1
  SCAN_SYMBOL = 2
  LOCAL_SCAN_SYMBOL = 3
  MANUAL_CLOSE_ORDER = 4

class LoggerType(Enum):
  CREATE_ORDER_FAILED = 'Create Order Failed'
  POLLING_ORDER_STATUS = 'Polling Order Status'
  OPEN_TRADE = 'Open Trade'
  OPEN_TRADE_FAILED = 'Open Trade Failed'
  ORDER_FILLED = 'Order Filled'
  TRADE_SUMMARY = 'Trade Summary'
  HOLDING_REPORT = 'Holding Report'
  CLOSE_TRADE_DETAIL = 'Close Trade Detail'
  INTERESTING_SYMBOL = 'Found Interesting Symbol'

buy_rsi = int(os.environ['OPEN_TRADE_UPCROSS_RSI'])
stoploss_rsi = int(os.environ['STOP_LOSS_DOWNCROSS_RSI'])
takeprofit_rsi = int(os.environ['TAKE_PROFIT_DOWNCROSS_RSI'])