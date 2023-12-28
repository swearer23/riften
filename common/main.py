import os
import json
from binance.spot import Spot

def get_all_quote_assets(exchange_info=None):
  if exchange_info is None:
    client = Spot()
    exchange_info = client.exchange_info()
  quote_assets = [item['quoteAsset'] for item in exchange_info['symbols']]
  return quote_assets

def get_all_symbols(quote_asset='USDT'):
  permissions = os.environ.get('TRADE_PERMISSION').split(',')
  client = Spot()
  exchange_info = client.exchange_info(permissions=permissions)
  quote_assets = list(set(get_all_quote_assets(exchange_info)))
  if quote_asset not in quote_assets:
    raise Exception(f'quote asset {quote_asset} is not in {quote_assets}')
  symbols = [
    item['symbol'] for item in exchange_info['symbols']
    if item['quoteAsset'] == quote_asset
  ]
  return symbols

def get_all_valid_symbols():
  symbols = get_all_symbols()
  return [symbol for symbol in symbols if symbol not in banned_symbols]

intervals = [
  # '1s',
  # '1m',
  # '3m',
  '5m',
  '15m',
  '30m',
  '1h',
  '2h',
  '4h',
  '6h',
  '8h',
  '12h',
  '1d',
  # '3d',
  # '1w',
  # '1M',
]

banned_symbols = [
  'BCCUSDT',
  'VENUSDT',
  'PAXUSDT',
  'BCHABCUSDT',
  'BCHSVUSDT',
  'BTTUSDT',
  'USDSUSDT',
  'NANOUSDT',
  'MITHUSDT',
  'USDSBUSDT',
  'GTOUSDT',
  'ERDUSDT',
  'NPXSUSDT',
  'COCOSUSDT',
  'TOMOUSDT',
  'MFTUSDT',
  'STORMUSDT',
  'BEAMUSDT',
  'HCUSDT',
  'MCOUSDT',
  'BULLUSDT',
  'BEARUSDT',
  'ETHBULLUSDT',
  'ETHBEARUSDT',
  'TCTUSDT',
  'EOSBULLUSDT',
  'EOSBEARUSDT',
  'XRPBULLUSDT',
  'XRPBEARUSDT',
  'STRATUSDT',
  'AIONUSDT',
  'BNBBULLUSDT',
  'BNBBEARUSDT',
  'XZCUSDT',
  'GXSUSDT',
  'LENDUSDT',
  'REPUSDT',
  'BKRWUSDT',
  'DAIUSDT',
  'AUDUSDT',
  'SRMUSDT',
  'BZRXUSDT',
  'YFIIUSDT',
  'NBSUSDT',
  'HNTUSDT',
  'DNTUSDT',
  'SUSDUSDT',
  'BTCSTUSDT',
  'RAMPUSDT',
  'EPSUSDT',
  'AUTOUSDT',
  'BTGUSDT',
  'MIRUSDT',
  'NUUSDT',
  'TORNUSDT',
  'KEEPUSDT',
  'TVKUSDT',
  'TRIBEUSDT',
  'POLYUSDT',
  'RGTUSDT',
  'MCUSDT',
  'ANYUSDT',
  'USTUSDT',
  'ANCUSDT',
  'NEBLUSDT',
  'BETHUSDT',
  'AEURUSDT',
  'JTOUSDT',
  '1000SATSUSDT',
  'BONKUSDT',
  'ACEUSDT'
]

def is_beginning_of_interval(now, interval):
  if interval == '1m':
    return now.second == 0
  elif interval == '5m':
    return now.second == 0 and now.minute % 5 == 0
  elif interval == '15m':
    return now.second == 0 and now.minute % 15 == 0
  elif interval == '30m':
    return now.second == 0 and now.minute % 30 == 0
  elif interval == '1h':
    return now.second == 0 and now.minute == 0
  elif interval == '2h':
    return now.second == 0 and now.minute == 0 and now.hour % 2 == 0
  elif interval == '4h':
    return now.second == 0 and now.minute == 0 and now.hour % 4 == 0
  elif interval == '6h':
    return now.second == 0 and now.minute == 0 and now.hour % 6 == 0
  elif interval == '8h':
    return now.second == 0 and now.minute == 0 and now.hour % 8 == 0
  elif interval == '12h':
    return now.second == 0 and now.minute == 0 and now.hour % 12 == 0
  elif interval == '1d':
    return now.second == 0 and now.minute == 0 and now.hour == 0
  else:
    raise Exception(f'unknown interval {interval}')
  
def beginning_of_interval(now, interval):
  if interval == '1m':
    return now.replace(second=0)
  elif interval == '5m':
    return now.replace(second=0, minute=now.minute - now.minute % 5)
  elif interval == '15m':
    return now.replace(second=0, minute=now.minute - now.minute % 15)
  elif interval == '30m':
    return now.replace(second=0, minute=now.minute - now.minute % 30)
  elif interval == '1h':
    return now.replace(second=0, minute=0)
  elif interval == '2h':
    return now.replace(second=0, minute=0, hour=now.hour - now.hour % 2)
  elif interval == '4h':
    return now.replace(second=0, minute=0, hour=now.hour - now.hour % 4)
  elif interval == '6h':
    return now.replace(second=0, minute=0, hour=now.hour - now.hour % 6)
  elif interval == '8h':
    return now.replace(second=0, minute=0, hour=now.hour - now.hour % 8)
  elif interval == '12h':
    return now.replace(second=0, minute=0, hour=now.hour - now.hour % 12)
  elif interval == '1d':
    return now.replace(second=0, minute=0, hour=0)
  else:
    raise Exception(f'unknown interval {interval}')