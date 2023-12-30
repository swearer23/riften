import os
from datetime import datetime
import pandas as pd
from utils import LoggerType, send_mail

class LoggerMixin:
  def trade_summary_logger(self, info, trades):
    self.print({
      'title': LoggerType.TRADE_SUMMARY,
      **info,
    })
    send_mail(
      title=f'[{datetime.now()}] Trade Summary',
      content=f'{pd.DataFrame([info]).to_html()}',
      mimetype='html'
    )
    for trade in trades:
      self.print({
        'title': LoggerType.CLOSE_TRADE_DETAIL,
        **trade
      })

  def holding_report_logger(self, **kwargs):
    self.print({
      'title': LoggerType.HOLDING_REPORT,
      **kwargs
    })

  def order_filled_logger(self, **kwargs):
    self.print({
      'title': LoggerType.ORDER_FILLED,
      **kwargs
    })
  
  def create_order_failed_logger(self, **kwargs):
    self.print({
      'title': LoggerType.CREATE_ORDER_FAILED,
      **kwargs
    })

  def open_trade_logger(self, **kwargs):
    self.print({
      'title': LoggerType.OPEN_TRADE,
      **kwargs
    })

  def open_trade_failed_logger(self, **kwargs):
    self.print({
      'title': LoggerType.OPEN_TRADE_FAILED,
      **kwargs
    })

  def polling_order_status_logger(self, **kwargs):
    self.print({
      'title': LoggerType.POLLING_ORDER_STATUS,
      **kwargs
    })

  def interesting_symbol_discovered_logger(self, **kwargs):
    self.print({
      'title': LoggerType.INTERESTING_SYMBOL,
      **kwargs
    })

  def print(self, data):
    dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['title'] = data['title'].value
    data['datetime'] = dt_str
    date_str = datetime.now().strftime("%Y-%m-%d")
    df = pd.DataFrame([data])
    print(f'[{dt_str}] ======================================:')
    print(df)
    path = f'./logs/{data["title"]}.{date_str}.csv'
    if not os.path.exists(path):
      df.to_csv(path, index=False)
    else:
      df.to_csv(path, mode='a', header=False, index=False)
    