""" Market watcher for CampBX.
"""

from utils import create_price_amount_list
from watcher import Watcher

class CampBXWatcher(Watcher):
  def __init__(self, override_refresh_time_sec=None):
    super(CampBXWatcher, self).__init__('CampBX', override_refresh_time_sec)
    self.url = 'http://campbx.com/api/xdepth.php'

  def _update_order_book_from_json(self, json_data):
    asks = create_price_amount_list(json_data, 'Asks', True)
    if asks is None:
      return False
    bids = create_price_amount_list(json_data, 'Bids', False)
    if bids is None:
      return False
    self.order_book = {'asks': asks, 'bids': bids}
    return True

