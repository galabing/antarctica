""" Base class of market watchers.

A market watcher talks to the API of a market to get the order book,
and perodically refreshes it to keep it up to date.
"""

import time
from config import refresh_time_sec, timeout_sec
from utils import read_json, validate_order_book

class Watcher(object):
  def __init__(self, market_name, override_refresh_time_sec=None):
    self.market_name = market_name
    self.last_update_timestamp_sec = 0
    self.dirty = False
    self.order_book = {}
    self.url = None  # market specific
    self.refresh_time_sec = refresh_time_sec
    # Used for testing.
    if override_refresh_time_sec is not None:
      self.refresh_time_sec = override_refresh_time_sec

  def get_order_book(self):
    """ Gets the up-to-date order book of the market, or None if there was
        an error getting the order book.
    """
    if (not self.dirty and
        time.time() - self.last_update_timestamp_sec < self.refresh_time_sec):
      return self.order_book
    timestamp_sec = self._refresh_order_book()
    if (timestamp_sec > self.last_update_timestamp_sec and
        validate_order_book(self.order_book)):
      self.last_update_timestamp_sec = timestamp_sec
      self.dirty = False
      return self.order_book
    return None

  def set_dirty(self):
    """ Marks the order book as dirty, eg, after a transaction is executed.

    This will force a refresh next time get_order_book() is called.
    """
    self.dirty = True

  def _refresh_order_book(self):
    timestamp_sec = time.time()
    json_data = read_json(self.url, timeout_sec)
    if json_data is not None and self._update_order_book_from_json(json_data):
      return timestamp_sec
    return 0

  def _update_order_book_from_json(self, json_data):
    """ Market-specific method to update the order book from the json
        object returned from the API request.

    Updates self.order_book if successful and returns True, or False if there
    was an error.
    """
    return False

