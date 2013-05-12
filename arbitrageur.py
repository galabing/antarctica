#!/usr/bin/python3

import argparse
import config
import logging
from arbitrage_detector import ArbitrageDetector
from market_watcher import MarketWatcher
from os import environ
from time import sleep, tzset

class Arbitrageur(object):
  def __init__(self):
    self.market_watcher = MarketWatcher()
    self.arbitrage_detector = ArbitrageDetector()

  def run(self):
    while True:
      order_books = self.market_watcher.get_order_books()
      logging.info('Received %d order books' % len(order_books))
      opportunities = self.arbitrage_detector.process(order_books)
      logging.info('Detected %d opportunities' % len(opportunities))
      for opportunity in opportunities:
        self._log_opportunity(opportunity)
      sleep(config.sleep_between_rounds_sec)

  def _log_opportunity(self, opportunity):
    buy_market = opportunity.buy_market
    sell_market = opportunity.sell_market
    buy_price = opportunity.weighted_buy_price / 100.0
    sell_price = opportunity.weighted_sell_price / 100.0
    amount = opportunity.amount / 100000000.0
    pay = opportunity.pay / 100.0
    paid = opportunity.paid / 100.0
    profit = paid - pay
    rate = 0.0
    # Sometimes the trading amount is so small (eg, 10 satoshis) that
    # the pay is rounded down to 0 cents.
    if pay > 0:
      rate = profit * 100 / pay
    marginal_rate = ((opportunity.min_sell_price - opportunity.max_buy_price) *
                     100.0) / opportunity.max_buy_price
    logging.info('Opportunity: buy=%.2f sell=%.2f from=%s to=%s amount=%.8f'
                 ' pay=%.2f paid=%.2f profit=%.2f rate=%.2f%% mrate=%.2f%%'
                 % (buy_price, sell_price, buy_market, sell_market, amount,
                    pay, paid, profit, rate, marginal_rate))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--verbose', action='store_true')
  args = parser.parse_args()
  environ['TZ'] = 'US/Pacific'
  tzset()
  level = logging.INFO
  if args.verbose:
    level = logging.DEBUG
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)
  arbitrageur = Arbitrageur()
  arbitrageur.run()

if __name__ == '__main__':
  main()

