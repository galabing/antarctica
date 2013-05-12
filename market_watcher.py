""" A watcher of the entire market (multiple exchanges).
"""

import config
import logging
from bad_watcher import BadWatcher
from bitstamp_watcher import BitstampWatcher
from btce_watcher import BTCEWatcher
from campbx_watcher import CampBXWatcher
from concurrent.futures import ThreadPoolExecutor, wait
from mtgox_watcher import MtGoxWatcher

class MarketWatcher(object):
  def __init__(self):
    """ Init a list of exchange watchers from the config file.
    """
    watcher_dict = {
        'bad': BadWatcher,
        'bitstamp': BitstampWatcher,
        'btce': BTCEWatcher,
        'campbx': CampBXWatcher,
        'mtgox': MtGoxWatcher
    }
    self.exchange_watchers = [watcher_dict[exchange]()
                              for exchange in config.exchanges]
    self.thread_pool = ThreadPoolExecutor(
        max_workers=len(self.exchange_watchers))

  def get_exchange_names(self):
    """ Returns a list of exchange names on this market.
    """
    return [watcher.exchange_name for watcher in self.exchange_watchers]

  def get_order_books(self):
    """ Returns a list of order books collected from the exchanges.

    If for some reason, an order book cannot be collected from an exchange
    (eg, the API service is unavailable at the moment), its order book will
    be skipped in the result.  The return value is a list of tuples, with
    each tuple containing an exchange name and its order book.
    """
    requests = [(watcher.exchange_name,
                 self.thread_pool.submit(watcher.get_order_book))
                for watcher in self.exchange_watchers]
    logging.info('Waiting on %d requests' % len(requests))
    wait([request[1] for request in requests])
    return [(request[0], request[1].result())
            for request in requests if request[1].result() is not None]

