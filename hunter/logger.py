import os
from datetime import datetime, timedelta
import pandas as pd
from utils import LoggerType, send_mail

class LoggerMixin:
  def trade_summary_logger(self, info, trades):
    self.print({
      'title': LoggerType.TRADE_SUMMARY,
      **info,
    })
    send_mail(
      title=f'{LoggerType.TRADE_SUMMARY} [{datetime.now()}]',
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
    log = {
      'title': LoggerType.OPEN_TRADE,
      **kwargs
    }
    self.print(log)
    send_mail(
      title=f'{LoggerType.OPEN_TRADE} [{datetime.now()}]',
      content=f'{pd.DataFrame([log]).to_html()}',
      mimetype='html'
    )

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

  def file_name_format(self):
    return "%Y-%m"

  def get_recent_trade_symbols(self):
    today = datetime.now()
    date_str = today.strftime(self.file_name_format())
    path = f'./logs/{LoggerType.TRADE_SUMMARY.value}.{date_str}.csv'
    if not os.path.exists(path):
      yesterday= today - timedelta(days=1)
      date_str = yesterday.strftime(self.file_name_format())
      path = f'./logs/{LoggerType.TRADE_SUMMARY}.{date_str}.csv'
    if not os.path.exists(path):
      return []
    df = pd.read_csv(path)
    df = df.sort_values(by=['datetime'], ascending=False)
    df = df[df['profit'] < 0]
    return df['symbol'].values.tolist()

  def print(self, data):
    dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['title'] = data['title'].value
    data['datetime'] = dt_str
    date_str = datetime.now().strftime(self.file_name_format())
    df = pd.DataFrame([data])
    print(f'[{dt_str}] ======================================:')
    print(df)
    path = f'./logs/{data["title"]}.{date_str}.csv'
    if not os.path.exists(path):
      df.to_csv(path, index=False)
    else:
      exiting = pd.read_csv(path).to_dict('records')
      new = df.to_dict('records')
      concat = exiting + new
      pd.DataFrame(concat).to_csv(path, header=True, index=False)
    