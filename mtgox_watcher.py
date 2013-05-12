""" Market watcher for MtGox.
"""

from exchange_watcher import ExchangeWatcher
import logging
from utils import convert_amount, convert_price

class MtGoxWatcher(ExchangeWatcher):
  def __init__(self):
    super(MtGoxWatcher, self).__init__('MtGox')
    self.url = 'http://data.mtgox.com/api/2/BTCUSD/money/depth'

  def _parse_order_book_from_json(self, json_data):
    if json_data.get('result', None) != 'success':
      logging.error('Request was not successful: %s' % json_data)
      return None
    order_book_data = json_data.get('data', None)
    if order_book_data is None:
      logging.error('Cannot find order book data: %s' % order_book_data)
      return None
    asks = self._create_price_amount_list(order_book_data, 'asks', True)
    if asks is None:
      return None
    bids = self._create_price_amount_list(order_book_data, 'bids', False)
    if bids is None:
      return None
    return {'asks': asks, 'bids': bids}

  def _create_price_amount_list(self, order_book_data, key, ascending):
    price_amount_data = order_book_data.get(key, None)
    if price_amount_data is None:
      logging.error('Cannot find price amount data for %s: %s' %
          key, order_book_data)
      return None
    try:
      price_amount_list = [
          (convert_price(data['price']), convert_amount(data['amount']))
          for data in price_amount_data]
    except KeyError:
      logging.error('KeyError in price-amount data: %s' % price_amount_data)
      return None
    price_amount_list.sort(key=lambda x: x[0], reverse=not ascending)
    return price_amount_list

