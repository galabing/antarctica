import unittest
from bitstamp_watcher import BitstampWatcher
from btce_watcher import BTCEWatcher
from campbx_watcher import CampBXWatcher
from mtgox_watcher import MtGoxWatcher
from utils import validate_order_book

class TestWatchers(unittest.TestCase):
  def test_bitstamp_watcher(self):
    self._test_watcher(BitstampWatcher())

  def test_btce_watcher(self):
    self._test_watcher(BTCEWatcher())

  def test_campbx_watcher(self):
    self._test_watcher(CampBXWatcher())

  def test_mtgox_watcher(self):
    self._test_watcher(MtGoxWatcher())

  def _test_watcher(self, watcher):
    """ Tests an exchange watcher by fetching an order book and verifying
        its validity.

    NOTE: This test WILL have transient failures as we are talking to the
          actual API service.
    TODO: Prefer to mock away the exchange API.
    """
    order_book = watcher.get_order_book()
    self.assertIsNotNone(order_book)
    self.assertTrue(validate_order_book(order_book))

if __name__ == '__main__':
  unittest.main()

