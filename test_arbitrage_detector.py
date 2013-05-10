import unittest
from arbitrage_detector import ArbitrageDetector, ArbitrageOpportunity

def _p(p):
  return int(round(p * 100))

def _a(a):
  return int(round(a * 100000000))

def _pa(p, a):
  return (_p(p), _a(a))

def _pal(p, a):
  return list(_pa(p, a))

class TestArbitrageDetector(unittest.TestCase):
  def setUp(self):
    self.detector = ArbitrageDetector(fixed_marginal_profit_rate=0)

  def test_has_matching_orders(self):
    self.assertFalse(self.detector.has_matching_orders(
        'Market', {'asks': [], 'bids': []}))
    self.assertFalse(self.detector.has_matching_orders(
        'Market', {'asks': [(1, 1)], 'bids': []}))
    self.assertFalse(self.detector.has_matching_orders(
        'Market', {'asks': [], 'bids': [(1, 1)]}))
    self.assertTrue(self.detector.has_matching_orders(
        'Market', {'asks': [(1, 2)], 'bids': [(1, 1)]}))
    self.assertFalse(self.detector.has_matching_orders(
        'Market', {
            'asks': [
                (7, 2),
                (8, 1),
            ],
            'bids': [
                (6, 3),
                (5, 2),
            ]
        }))
    self.assertTrue(self.detector.has_matching_orders(
        'Market', {
            'asks': [
                (7, 2),
                (8, 1),
            ],
            'bids': [
                (7, 3),
                (6, 3),
            ]
        }))
    self.assertTrue(self.detector.has_matching_orders(
        'Market', {
            'asks': [
                (7, 2),
                (8, 1),
            ],
            'bids': [
                (10, 3),
            ]
        }))

  def test_process_pair(self):
    self.assertIsNone(self.detector.process_pair('buy', 'sell', [], []))
    self.assertIsNone(self.detector.process_pair('buy', 'sell', [(1, 1)], []))
    self.assertIsNone(self.detector.process_pair('buy', 'sell', [], [(1, 1)]))
    self.assertIsNone(self.detector.process_pair('buy', 'sell',
        [(3, 3), (4, 4)], [(2, 2), (1, 1)]))
    self.assertIsNone(self.detector.process_pair('buy', 'sell',
        [(2, 2), (3, 3)], [(2, 2), (1, 1)]))

    asks = [_pa(2, 1), _pa(3, 1), _pa(4, 1), _pa(5, 1)]
    bids = [_pa(5, 1), _pa(4, 1), _pa(3, 1), _pa(2, 1)]
    expected_opportunity = ArbitrageOpportunity(
        'BuyMarket', 'SellMarket',
        [_pa(2, 1), _pa(3, 1)], [_pa(5, 1), _pa(4, 1)],
        _p(2), _p(3), _p(2.5), _p(4), _p(5), _p(4.5),
        _a(2), _p(5), _p(9))
    self.assertEqual(
        expected_opportunity,
        self.detector.process_pair('BuyMarket', 'SellMarket', asks, bids))

    asks = [_pa(2, 2), _pa(3, 2), _pa(4, 1), _pa(5, 2)]
    bids = [_pa(6, 1), _pa(5, 5), _pa(4, 2), _pa(2, 1)]
    expected_opportunity = ArbitrageOpportunity(
        'BuyMarket', 'SellMarket',
        [_pa(2, 2), _pa(3, 2), _pa(4, 1)],
        [_pa(6, 1), _pa(5, 4)],
        _p(2), _p(4), _p(2.8), _p(5), _p(6), _p(5.2),
        _a(5), _p(14), _p(26))
    self.assertEqual(
        expected_opportunity,
        self.detector.process_pair('BuyMarket', 'SellMarket', asks, bids))

  def test_process_pair_high_margin(self):
    detector = ArbitrageDetector(fixed_marginal_profit_rate=0.3)
    # This is the same input as the last case in test_process_pair(),
    # except that now the marginal profit rate is 0.3, and the last
    # bitcoin from buying at 4 and selling at 5 does not qualify any more
    # (profit is 0.25).
    asks = [_pa(2, 2), _pa(3, 2), _pa(4, 1), _pa(5, 2)]
    bids = [_pa(6, 1), _pa(5, 5), _pa(4, 2), _pa(2, 1)]
    expected_opportunity = ArbitrageOpportunity(
        'BuyMarket', 'SellMarket',
        [_pa(2, 2), _pa(3, 2)], [_pa(6, 1), _pa(5, 3)],
        _p(2), _p(3), _p(2.5), _p(5), _p(6), _p(5.25),
        _a(4), _p(10), _p(21))
    self.assertEqual(
        expected_opportunity,
        detector.process_pair('BuyMarket', 'SellMarket', asks, bids))

if __name__ == '__main__':
  unittest.main()

