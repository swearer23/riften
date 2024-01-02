from datetime import datetime
from multiprocessing import Pool, cpu_count
from hunter.account import BNAccount
from hunter.models.SymbolList import SymbolList
from hunter.models.Symbol import ActiveSymbol
from hunter.trade import BinaceTradingBot
from common import beginning_of_interval
from hunter.prepare_data import fetch_data, get_active_symbols
from hunter.models.Holding import Holding
from hunter.models.Position import Position, PositionCloseReason
from hunter.logger import LoggerMixin

class TaskImpl(LoggerMixin):
  def __init__(
      self,
      account: BNAccount,
      symbol_list: SymbolList,
      bot: BinaceTradingBot
    ):
    self.account = account
    self.symbol_list = symbol_list
    self.bot = bot

  def init_holding(self):
    Holding.init_holdings(self.account, self.symbol_list)

  def clear_holdings(self) -> bool:
    if Holding.get_active_holding_len() == 0:
      return True
    else:
      position_list = [
        Position(**x) for x in Holding.get_all_active_holding()
      ]
      for position in position_list:
        position.try_to_close()
      return Holding.get_active_holding_len() == 0
    
  def get_active_position(self):
    active_positions = [
      Position(**x) for x in Holding.get_all_active_holding()
    ]
    if len(active_positions) == 0:
      return None
    else:
      return active_positions[0]

  def scan_interesting_symbol(self, interval) -> list[ActiveSymbol]:
    print('scan interesting symbol')
    # now = datetime(2023, 12, 26, 18, 40)
    now = datetime.now()
    end = beginning_of_interval(now, interval)
    all_symbols = self.symbol_list.get_all_symbols()
    active_symbols = []
    step = cpu_count()
    for idx in range(0, len(all_symbols), step):
      result = Pool(cpu_count()).map(
        fetch_data,
        [
          (symbol.symbol, interval, end)
          for symbol in all_symbols[idx:idx+step]
        ]
      )
      res = []
      for r in result:
        res.append((r[0], self.symbol_list.find_by_symbol_name(r[1])))
      active_symbols += get_active_symbols(res)
    return active_symbols
  
  def new_round(self, interval):
    holdings_cleared = self.clear_holdings()
    active_symbols = self.scan_interesting_symbol(interval)
    if len(active_symbols) > 0:
      if holdings_cleared:
        self.open_trade(self.choose_symbol_to_open(active_symbols))
      for symbol in active_symbols:
        self.interesting_symbol_discovered_logger(
          symbol=symbol.symbol,
          interval=symbol.interval,
          price=symbol.price,
          rsi_14=symbol.rsi_14,
          surge_factor=symbol.get_surge_factor(),
        )
    self.rebalance(active_symbols)
  
  def rebalance(self, active_symbols: list[ActiveSymbol]):
    active_position = self.get_active_position()
    if active_position and active_position.get_curr_profit() < 0:
      better_symbol = self.found_better_symbol(active_symbols)
      if better_symbol:
        active_position.try_to_close(reason=PositionCloseReason.REBALANCE)
        self.open_trade(better_symbol)

  def found_better_symbol(self, interesting_symbols: list[ActiveSymbol]):
    better_last_upcross_rsi_symbols = self.find_better_last_upcross_rsi_symbols(interesting_symbols)
    better_surge_symbols = self.find_better_surge_symbols(interesting_symbols)
    inter = set(better_last_upcross_rsi_symbols).intersection(set(better_surge_symbols))
    if len(inter) > 0:
      return list(inter)[0]
    elif len(better_surge_symbols) > 0:
      return better_surge_symbols[0]
    elif len(better_last_upcross_rsi_symbols) > 0:
      return better_last_upcross_rsi_symbols[0]
    else:
      return None

  def find_better_last_upcross_rsi_symbols(self, interesting_symbols: list[ActiveSymbol]):
    better_symbols = [x for x in interesting_symbols if x.get_last_upcross_buy_rsi() > 30]
    return better_symbols
    
  def find_better_surge_symbols(self, interesting_symbols: list[ActiveSymbol]):
    better_symbols = [x for x in interesting_symbols if 5 > x.get_surge_factor() > 2]
    if len(better_symbols) > 0:
      better_symbols = sorted(
        better_symbols,
        key=lambda x: x.get_surge_factor(),
        reverse=True
      )
    return better_symbols

  def choose_symbol_to_open(self, active_symbols: list[ActiveSymbol]):
    recent_symbols = self.get_recent_trade_symbols()
    for symbol in recent_symbols:
      if symbol in [x.symbol for x in active_symbols]:
        find_index = [x.symbol for x in active_symbols].index(symbol)
        return active_symbols[find_index]

    # sort by surge factor, choose the highest one
    active_symbols = sorted(
      active_symbols,
      key=lambda x: x.get_surge_factor(),
      reverse=True
    )

    optimized_active_symbols = [
      x for x in active_symbols
      if 2 < x.get_surge_factor() < 5
    ]

    if len(optimized_active_symbols) > 0:
      return optimized_active_symbols[0]

    return active_symbols[0]

  def open_trade(self, symbol):
    self.bot.open_trade(symbol)

  def manual_close(self, order_id):
    position = Position(**Holding.get_active_holding_by_id(order_id))
    position.close()
