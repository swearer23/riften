from binance.spot import Spot

def get_all_base_assets(exchange_info=None):
  if exchange_info is None:
    client = Spot()
    exchange_info = client.exchange_info()
  base_assets = [item['baseAsset'] for item in exchange_info['symbols']]
  return base_assets

def get_all_quote_assets(exchange_info=None):
  if exchange_info is None:
    client = Spot()
    exchange_info = client.exchange_info()
  quote_assets = [item['quoteAsset'] for item in exchange_info['symbols']]
  return quote_assets

def get_all_symbols(quote_asset='USDT'):
  client = Spot()
  exchange_info = client.exchange_info()
  quote_assets = list(set(get_all_quote_assets(exchange_info)))
  if quote_asset not in quote_assets:
    raise Exception(f'quote asset {quote_asset} is not in {quote_assets}')
  symbols = [
    item['symbol'] for item in exchange_info['symbols']
    if item['quoteAsset'] == quote_asset
  ]
  return symbols

intervals = [
  # '1s',
  '1m',
  '3m',
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