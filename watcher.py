""" Base class for exchange watchers.

An exchange watcher talks to the API service of an exchange to get the most
up-to-date and valid order book.
"""

from utils import read_json, validate_order_book

class Watcher(object):
  def __init__(self, exchange_name):
    self.exchange_name = exchange_name

  def get_order_book(self):
    """ Gets the up-to-date and valid order book of the exchange, or None if
        there was a problem (eg, the API service was unavailable at the
        moment or the returned order book was invalid).
    """
    # The URL for the API service is exchange-specific and should have been
    # inited by subclasses.
    json_data = read_json(self.url)
    if json_data is None:
      return None
    order_book = self._parse_order_book_from_json(json_data)
    if order_book is None or not validate_order_book(order_book):
      return None
    return order_book

  def _parse_order_book_from_json(self, json_data):
    """ Exchange-specific method to parse the order book from the json
        object returned from the API request.
    """
    pass

