""" Market watcher for Bitstamp.
"""

from exchange_watcher import ExchangeWatcher
from utils import create_price_amount_list

class BitstampWatcher(ExchangeWatcher):
  def __init__(self):
    super(BitstampWatcher, self).__init__('Bitstamp')
    self.url = 'https://www.bitstamp.net/api/order_book/'

  def _parse_order_book_from_json(self, json_data):
    asks = create_price_amount_list(json_data, 'asks', True)
    if asks is None:
      return None
    bids = create_price_amount_list(json_data, 'bids', False)
    if bids is None:
      return None
    return {'asks': asks, 'bids': bids}

