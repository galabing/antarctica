""" Market watcher for nothing, fails everytime when _refresh_order_book() is
    called (returns 0).

This is used for testing only to ensure that the arbitrageur can live with
transient market unavailability.
"""

import logging
from watcher import Watcher

class BadWatcher(Watcher):
  def __init__(self):
    super(BadWatcher, self).__init__('Bad', 0, 0)

  def _refresh_order_book(self):
    logging.debug('Bad market watcher, returning 0.')
    return 0

