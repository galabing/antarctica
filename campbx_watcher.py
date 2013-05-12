""" Market watcher for CampBX.
"""

from utils import create_price_amount_list
from watcher import Watcher

class CampBXWatcher(Watcher):
  def __init__(self):
    super(CampBXWatcher, self).__init__('CampBX')
    self.url = 'http://campbx.com/api/xdepth.php'

  def _parse_order_book_from_json(self, json_data):
    asks = create_price_amount_list(json_data, 'Asks', True)
    if asks is None:
      return None
    bids = create_price_amount_list(json_data, 'Bids', False)
    if bids is None:
      return None
    return {'asks': asks, 'bids': bids}

