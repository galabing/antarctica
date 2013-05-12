""" Market watcher for BTC-E.
"""

from utils import create_price_amount_list
from watcher import Watcher

class BTCEWatcher(Watcher):
  def __init__(self):
    super(BTCEWatcher, self).__init__('BTC-E')
    self.url = 'https://btc-e.com/api/2/btc_usd/depth'

  def _parse_order_book_from_json(self, json_data):
    asks = create_price_amount_list(json_data, 'asks', True)
    if asks is None:
      return None
    bids = create_price_amount_list(json_data, 'bids', False)
    if bids is None:
      return None
    return {'asks': asks, 'bids': bids}

