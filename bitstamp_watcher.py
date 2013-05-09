""" Market watcher for Bitstamp.
"""

from utils import create_price_amount_list
from watcher import Watcher

class BitstampWatcher(Watcher):
  def __init__(self, override_refresh_time_sec=None):
    super(BitstampWatcher, self).__init__('Bitstamp', override_refresh_time_sec)
    self.url = 'https://www.bitstamp.net/api/order_book/'

  def _update_order_book_from_json(self, json_data):
    asks = create_price_amount_list(json_data, 'asks', True)
    if asks is None:
      return False
    bids = create_price_amount_list(json_data, 'bids', False)
    if bids is None:
      return False
    self.order_book = {'asks': asks, 'bids': bids}
    return True

