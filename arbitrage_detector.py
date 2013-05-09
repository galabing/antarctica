""" A detector for arbitrage opportunities.

It takes order books from different markets, and detects buy-low-sell-high
opportunities among them.
"""

import logging

class ArbitrageOpportunity(object):
  def __init__(self, buy_market, sell_market, buys, sells,
               min_buy_price, max_buy_price, weighted_buy_price,
               min_sell_price, max_sell_price, weighted_sell_price,
               amount, pay, paid):
    # All the price data is in cents, and amount data in satoshis.
    self.buy_market = buy_market
    self.sell_market = sell_market
    self.buys = buys
    self.sells = sells
    self.min_buy_price = min_buy_price
    self.max_buy_price = max_buy_price
    self.weighted_buy_price = weighted_buy_price
    self.min_sell_price = min_sell_price
    self.max_sell_price = max_sell_price
    self.weighted_sell_price = weighted_sell_price
    self.amount = amount
    self.pay = pay
    self.paid = paid

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.__dict__ == other.__dict__
    return False

  def __ne__(self, other):
    return not self.__eq__(other)

  def __str__(self):
    return '%s' % self.__dict__

class ArbitrageDetector(object):
  def __init__(self, marginal_profit_rate, ignore_matching_orders=False):
    """
    Args:
      marginal_profit_rate: The profit rate ((sell - buy) / buy) beyond which
                            trading volume can be increased.
      ignore_matching_orders: If True, matching orders within each order book
                              are ignored and the corresponding order books are
                              considered valid.  Otherwise, the order books with
                              matching orders are considered invalid and are not
                              used for detecting arbitrage opportunities.

    TODO: Run with prematch_order_books=True and log how often order books
          have matching orders, and find out if they are due to processing
          lags or special order rules (eg, AON orders).
    """
    assert marginal_profit_rate >= 0
    self.marginal_profit_rate = marginal_profit_rate
    self.ignore_matching_orders = ignore_matching_orders

  def process(self, order_books):
    """
    Args:
      order_books: A list of (market_name, order_book) tuples.  Each order book
                   should have been converted and validated (ie, the prices are
                   in cents and the amounts are in satoshis; asks and bids are
                   properly ordered etc).
    Returns: A list of arbitrage opportunities.
    """
    if not self.ignore_matching_orders:
      order_books = [(item[0], item[1]) for item in order_books
          if not self.has_matching_orders(item[0], item[1])]
    logging.info('Processing %d order books' % len(order_books))
    opportunities = []
    for i in range(len(order_books)):
      for j in range(len(order_books)):
        if i == j:
          continue
        opportunity = self.process_pair(
            order_books[i][0], order_books[j][0],
            order_books[i][1]['asks'], order_books[j][1]['bids'])
        if opportunity is not None:
          logging.debug('Found opportunity: %s' % opportunity)
          opportunities.append(opportunity)
    return opportunities

  def has_matching_orders(self, market_name, order_book):
    """ Detects whether an order book contains matching orders
        (ie, asking price <= bidding price).
    """
    # Since the asks and bids are properly ordered, we only need to look at
    # the first entry, if exists.
    asks, bids = order_book['asks'], order_book['bids']
    if len(asks) == 0 or len(bids) == 0:
      return False
    matching = asks[0][0] <= bids[0][0]
    if matching:
      logging.warning('Detected matching orders in %s: %s' %
          (market_name, order_book))
    return matching

  def process_pair(self, buy_market, sell_market, asks, bids):
    """ Detects and returns arbitrage opportunity from buying low in one market
        ('asks') and selling high in the other ('bids'), or None if there is
        no such opportunity.
    """
    if len(asks) == 0 or len(bids) == 0:
      return None
    # Limit the asks and bids of interest to the top entries.  Specifically,
    # we do not care about asks above the first (highest) bid or bids below
    # the first (lowest) ask.
    # TODO: This is a bit awkward; maybe should use lists everywhere.
    good_asks = [list(ask) for ask in asks if ask[0] < bids[0][0]]
    good_bids = [list(bid) for bid in bids if bid[0] > asks[0][0]]
    if len(good_asks) == 0 or len(good_bids) == 0:
      return None
    # Walk down both lists and increase the trading volume as long as the
    # marginal profit rate is satisfied.
    i, j = 0, 0
    buys, sells = [], []
    while True:
      if i >= len(good_asks) or j >= len(good_bids):
        break
      profit_rate = (good_bids[j][0] - good_asks[i][0]) / good_asks[i][0]
      if profit_rate <= self.marginal_profit_rate:
        break
      if good_asks[i][1] < good_bids[j][1]:
        buys.append((good_asks[i][0], good_asks[i][1]))
        sells.append((good_bids[j][0], good_asks[i][1]))
        good_bids[j][1] -= good_asks[i][1]
        i += 1
      elif good_asks[i][1] > good_bids[j][1]:
        buys.append((good_asks[i][0], good_bids[j][1]))
        sells.append((good_bids[j][0], good_bids[j][1]))
        good_asks[i][1] -= good_bids[j][1]
        j += 1
      else:
        buys.append((good_asks[i][0], good_asks[i][1]))
        sells.append((good_bids[j][0], good_bids[j][1]))
        i += 1
        j += 1
    return self._process_buys_sells(buy_market, sell_market, buys, sells)

  def _process_buys_sells(self, buy_market, sell_market, buys, sells):
    assert len(buys) == len(sells)
    assert all([buys[i][1] == sells[i][1] for i in range(len(buys))])
    if len(buys) == 0:
      return None
    consolidated_buys, consolidated_sells = [list(buys[0])], [list(sells[0])]
    amount = buys[0][1]
    pay = buys[0][0] * amount
    paid = sells[0][0] * amount
    for i in range(1, len(buys)):
      if buys[i][0] == consolidated_buys[-1][0]:
        consolidated_buys[-1][1] += buys[i][1]
      else:
        assert buys[i][0] > consolidated_buys[-1][0]
        consolidated_buys.append(list(buys[i]))
      if sells[i][0] == consolidated_sells[-1][0]:
        consolidated_sells[-1][1] += sells[i][1]
      else:
        assert sells[i][0] < consolidated_sells[-1][0]
        consolidated_sells.append(list(sells[i]))
      amount += buys[i][1]
      pay += buys[i][0] * buys[i][1]
      paid += sells[i][0] * sells[i][1]
    divider = 100000000.0
    return ArbitrageOpportunity(
        buy_market, sell_market,
        [tuple(buy) for buy in consolidated_buys],
        [tuple(sell) for sell in consolidated_sells],
        buys[0][0], buys[-1][0], self._round(pay/float(amount)),
        sells[-1][0], sells[0][0], self._round(paid/float(amount)),
        amount, self._round(pay/divider), self._round(paid/divider))

  def _round(self, value):
    return int(round(value))

