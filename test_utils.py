import unittest
from utils import convert_amount, convert_price, read_json, validate_order_book

def _pa(p, a):
  return (int(p * 100), int(a * 100000000))

class TestUtils(unittest.TestCase):
  def test_read_json_fails_nicely(self):
    self.assertIsNone(read_json('https://www.google.com/', 2))
    self.assertIsNone(read_json('http://hopefullyneverarealurl.com/', 2))

  def test_convert_price(self):
    self.assertEqual(9800, convert_price(98))
    self.assertEqual(9800, convert_price(98.0))
    self.assertEqual(9800, convert_price('98.0'))
    self.assertIsNone(convert_price('$98'))

  def test_convert_amount(self):
    self.assertEqual(100000000, convert_amount(1))
    self.assertEqual(1000000000, convert_amount(10.0))
    self.assertEqual(12345678, convert_amount(0.12345678))
    self.assertEqual(12345678, convert_amount('0.12345678'))
    self.assertIsNone(convert_amount('1B'))

  def test_validate_order_book_empty(self):
    self.assertTrue(validate_order_book({'asks': [], 'bids': []}))

  def test_validate_order_book_small(self):
    self.assertTrue(validate_order_book({
        'asks': [_pa(98.0, 1.0)], 'bids': [_pa(96.0, 10.0)]}))

  def test_validate_order_book_normal(self):
    order_book = {
        'asks': [
            _pa(98.0, 1.0),
            _pa(98.2, 1.5),
            _pa(98.2, 0.5),
            _pa(99.4, 100.0)
        ],
        'bids': [
            _pa(99.6, 3.0),
            _pa(98.5, 5.0),
            _pa(98.5, 2.0),
            _pa(97.6, 0.1),
            _pa(96.0, 10.0)
        ]
    }
    self.assertTrue(validate_order_book(order_book))

  def test_validate_order_book_missing_key(self):
    self.assertFalse(validate_order_book({
        'asks': [_pa(98.0, 1.0)]}))

  def test_validate_order_book_unknown_key(self):
    self.assertFalse(validate_order_book({
        'asks': [], 'bids': [], 'borrows': [_pa(98.0, 1.0)]}))

  def test_validate_order_book_wrong_order(self):
    self.assertFalse(validate_order_book({
        'asks': [_pa(98.2, 1.5), _pa(98.0, 1.0)], 'bids': []}))
    self.assertFalse(validate_order_book({
        'asks': [], 'bids': [_pa(98.5, 5.0), _pa(99.6, 3.0)]}))

  def test_validate_order_book_wrong_size(self):
    self.assertFalse(validate_order_book({
        'asks': [(9800, 100000000, 1)], 'bids': []}))

  def test_validate_order_book_wrong_type(self):
    self.assertFalse(validate_order_book({
        'asks': [(9800, '100000000')], 'bids': []}))
    self.assertFalse(validate_order_book({
        'asks': [(98.0, 100000000)], 'bids': []}))

if __name__ == '__main__':
  unittest.main()

