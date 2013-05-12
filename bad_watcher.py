""" Market watcher for nothing, with no URL for API service defined.

This is used for testing only to ensure that the arbitrageur can live with
transient exchange unavailability.
"""

import logging
from watcher import Watcher

class BadWatcher(Watcher):
  def __init__(self):
    super(BadWatcher, self).__init__('Bad')
    self.url = ''

