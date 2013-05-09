#!/usr/bin/python3

import argparse
import logging
from arbitrage_detector import ArbitrageDetector
from bitstamp_watcher import BitstampWatcher
from btce_watcher import BTCEWatcher
from campbx_watcher import CampBXWatcher
from concurrent.futures import ThreadPoolExecutor, wait
from mtgox_watcher import MtGoxWatcher
from os import environ
from time import sleep, tzset

class Arbitrageur(object):
  def __init__(self, refresh_time_sec, timeout_sec, marginal_profit_rate,
               debug_watchers=False):
    self.refresh_time_sec = refresh_time_sec
    self.timeout_sec = timeout_sec
    self.marginal_profit_rate = marginal_profit_rate
    self.debug_watchers = debug_watchers

  def run(self):
    # TODO: Adjust per-market refresh rate according to market activity
    #       and throttle limit.
    self.market_watchers = [
        BitstampWatcher(self.refresh_time_sec, self.timeout_sec),
        BTCEWatcher(self.refresh_time_sec, self.timeout_sec),
        CampBXWatcher(self.refresh_time_sec, self.timeout_sec),
        MtGoxWatcher(self.refresh_time_sec, self.timeout_sec)]
    if self.debug_watchers:
      from bad_watcher import BadWatcher
      self.market_watchers.append(BadWatcher())
    self.thread_pool = ThreadPoolExecutor(
        max_workers=len(self.market_watchers))
    self.arbitrage_detector = ArbitrageDetector(self.marginal_profit_rate)
    self._loop()

  def _loop(self):
    while True:
      requests = [(watcher.market_name,
                   self.thread_pool.submit(watcher.get_order_book))
                  for watcher in self.market_watchers]
      logging.info('Waiting on %d requests' % len(requests))
      wait([request[1] for request in requests])
      order_books = [(request[0], request[1].result())
                     for request in requests
                     if request[1].result() is not None]
      logging.info('Received %d order books' % len(order_books))
      opportunities = self.arbitrage_detector.process(order_books)
      logging.info('Detected %d opportunities' % len(opportunities))
      # TODO: Move this out as an observer of this class.
      for opportunity in opportunities:
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
        marginal_rate = 100 * (opportunity.min_sell_price -
                         opportunity.max_buy_price) / opportunity.max_buy_price
        logging.info('Opportunity: buy=%.2f sell=%.2f from=%s to=%s amount=%.8f'
                     ' pay=%.2f paid=%.2f profit=%.2f rate=%.2f%% mrate=%.2f%%'
                     % (buy_price, sell_price, buy_market, sell_market, amount,
                        pay, paid, profit, rate, marginal_rate))
      # TODO: This is for the convenience of debugging.
      sleep(20)

def main():
  parser = argparse.ArgumentParser()
  # TODO: Adjust default settings.
  parser.add_argument('--refresh_time_sec', type=int, default=0)
  parser.add_argument('--timeout_sec', type=int, default=20)
  parser.add_argument('--marginal_profit_rate', type=float, default=0)
  parser.add_argument('--verbose', action='store_true')
  parser.add_argument('--debug_watchers', action='store_true')
  args = parser.parse_args()
  environ['TZ'] = 'US/Pacific'
  tzset()
  level = logging.INFO
  if args.verbose:
    level = logging.DEBUG
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)
  arbitrageur = Arbitrageur(args.refresh_time_sec,
                            args.timeout_sec,
                            args.marginal_profit_rate,
                            debug_watchers=args.debug_watchers)
  arbitrageur.run()

if __name__ == '__main__':
  main()

