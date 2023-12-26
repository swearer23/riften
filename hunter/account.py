from hunter.bnclient import BNClient

class BNAccount:
  def __init__(self) -> None:
    self.bnclient = BNClient()

  def get_balance(self, asset='USDT'):
    balences = self.bnclient.client.get_account()['balances']
    for item in balences:
      if item['asset'] == asset:
        return float(item['free'])