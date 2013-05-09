import unittest
from bitstamp_watcher import BitstampWatcher
from btce_watcher import BTCEWatcher
from campbx_watcher import CampBXWatcher
from mtgox_watcher import MtGoxWatcher
from utils import validate_order_book

class TestWatchers(unittest.TestCase):
  def setUp(self):
    self.refresh_time_sec = 20
    self.timeout_sec = 20

  def test_bitstamp_watcher(self):
    self._test_watcher(BitstampWatcher(self.refresh_time_sec, self.timeout_sec))

  def test_btce_watcher(self):
    self._test_watcher(BTCEWatcher(self.refresh_time_sec, self.timeout_sec))

  def test_campbx_watcher(self):
    self._test_watcher(CampBXWatcher(self.refresh_time_sec, self.timeout_sec))

  def test_mtgox_watcher(self):
    self._test_watcher(MtGoxWatcher(self.refresh_time_sec, self.timeout_sec))

  def _test_watcher(self, watcher):
    """ Tests a market watcher: Checks its preconditions, fetches an order book,
        verifies the validity of the order book, does another fetch and checks
        that the first result is reused (because the refresh time limit is not
        reached), marks the order book dirty, checks that a refetch is forced.

    NOTE: This test WILL have transient failures as we are talking to the actual
          market API.
    TODO: Prefer to mock away the market API.
    """
    # Check preconditions.
    self.assertEqual(watcher.last_update_timestamp_sec, 0)
    self.assertFalse(watcher.dirty)
    self.assertEqual(watcher.order_book, {})

    # Fetch order book for the first time.
    order_book = watcher.get_order_book()
    self.assertTrue(validate_order_book(order_book))
    # Further check that the order book is not empty (that is possible
    # but rare).
    self.assertNotEqual(order_book['asks'], [])
    self.assertNotEqual(order_book['bids'], [])

    # Check postconditions.
    # TODO: Prefer to use a mock time.
    self.assertGreater(watcher.last_update_timestamp_sec, 0)
    self.assertFalse(watcher.dirty)

    # Cache the current state of market watcher.
    old_order_book = order_book
    old_timestamp_sec = watcher.last_update_timestamp_sec

    # Do a second fetch.  The watcher should reuse the result of the first
    # fetch as the refresh time limit is not reached.
    new_order_book = watcher.get_order_book()
    self.assertEqual(new_order_book, old_order_book)
    self.assertEqual(watcher.last_update_timestamp_sec, old_timestamp_sec)
    self.assertFalse(watcher.dirty)

    # Mark the order book dirty.  This should force a refetch.
    watcher.set_dirty()
    self.assertTrue(watcher.dirty)
    order_book = watcher.get_order_book()
    self.assertTrue(validate_order_book(order_book))
    # Further check that the order book is not empty (that is possible
    # but rare).
    self.assertNotEqual(order_book['asks'], [])
    self.assertNotEqual(order_book['bids'], [])

    # Check that the timestamp has advanced and the order book is not dirty.
    self.assertGreater(watcher.last_update_timestamp_sec, old_timestamp_sec)
    self.assertFalse(watcher.dirty)

if __name__ == '__main__':
  unittest.main()

