""" Utility functions for the arbitrageur program.
"""

import config
import json
import logging
from socket import timeout
from urllib.request import URLError, urlopen

def read_json(url):
  """ Opens URL and returns the parsed json object, or None if failed.
  """
  try:
    text = urlopen(url, None, config.timeout_sec).read().decode('utf8')
  except URLError:
    logging.error('Failed to open url: %s' % url)
    return None
  except timeout:
    logging.error('Socket timed out: %s' % url)
    return None
  except Exception as ex:
    # TODO: This is for ConnectionResetError, and maybe there are others
    #       buried in the urlopen(), read() and decode() methods.
    #       Prefer not to use general Exception.
    logging.error('Failed to load content from url %s: %s' % (url, str(ex)))
    return None
  try:
    data = json.loads(text)
  except Exception:
    logging.error('Failed to parse the content of %s: %s' % (url, text))
    return None
  return data

def _convert_value(value, identifier, multiplier):
  try:
    return int(round(float(value) * multiplier, 0))
  except ValueError:
    logging.error('ValueError in converting %s: %s' % (identifier, value))
    return None

def convert_price(price):
  """ Converts a price (eg, 12.34) to cents (int 1234), or None if
      there was a conversion error.

  TODO: MtGox supports a max of five decimal points for prices.
        Figure out whether we should do anything about it.
  """
  return _convert_value(price, 'price', 100)

def convert_amount(amount):
  """ Converts a bitcoin amount (eg, 0.12345678) to satoshis
      (int 12345678), or None if there was a conversion error.
  """
  return _convert_value(amount, 'amount', 100000000)

def create_price_amount_list(order_book_data, key, ascending):
  """ Creates and returns the price-amount list from order book data,
      or None if the list could not be created.

  The order book data should be a dict extracted from the json object.
  The 'key' specifies the entry of interest in the order book (eg, 'asks'),
  and 'ascending' specifies the desired order of price in the output list.

  This method can be used to handle several API sources in the format of:
      {'asks': [[p0, a0], [p1, a1], ...],
       'bids': [[p0, a0], [p1, a1], ...]}
  """
  price_amount_data = order_book_data.get(key, None)
  if price_amount_data is None:
    logging.error('Cannot find price amount data for %s: %s' %
        (key, order_book_data))
    return None
  try:
    price_amount_list = [(convert_price(data[0]), convert_amount(data[1]))
        for data in price_amount_data]
  except ValueError:
    logging.error('ValueError in price-amount list: %s' % price_amount_data)
    return None
  price_amount_list.sort(key=lambda x: x[0], reverse=not ascending)
  return price_amount_list

def _validate_price_amount_list(pa_list, ascending):
  if len(pa_list) == 0:
    return True
  di, dj = 0, 1
  if not ascending:
    di, dj = 1, 0
  ok = all([len(pa_list[i]) == 2 and
            isinstance(pa_list[i][0], int) and
            isinstance(pa_list[i][1], int) and
            pa_list[i][0] > 0 and
            pa_list[i][1] > 0 and
            pa_list[i+di][0] <= pa_list[i+dj][0]
            for i in range(len(pa_list) - 1)])
  if not ok:
    return False
  # Check the last entry.
  return (len(pa_list[-1]) == 2 and
          isinstance(pa_list[-1][0], int) and
          isinstance(pa_list[-1][1], int) and
          pa_list[-1][0] > 0 and
          pa_list[-1][1] > 0)

def validate_order_book(order_book):
  """ Validates an order book, returns True if it is valid, False otherwise.

  An order book is a dictionary with two entries: 'asks' and 'bids', each of
  which mapped to a list of (price, amount) tuples.  The 'asks' list should
  be sorted by ascending prices, while the 'bids' list should be sorted by
  descending prices.  As an arbitrageur, we are interested in the lowest
  buying prices and highest selling prices, the top entries of both lists.
  Prices and amounts should be sane numbers (positive int after conversion).
  """
  if (len(order_book) != 2 or
      'asks' not in order_book or
      'bids' not in order_book):
    return False
  if not _validate_price_amount_list(order_book['asks'], ascending=True):
    return False
  return _validate_price_amount_list(order_book['bids'], ascending=False)

