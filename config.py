""" General configuration for the arbitrageur.
"""

# The participating markets.
markets = ('bitstamp', 'btce', 'campbx', 'mtgox')

# The main thread sleeps for a while between rounds.
# TODO: Adjust this value by the throttle limit of the exchanges.
sleep_between_rounds_sec = 20
# This is to prevent the market watchers from being throttled by setting
# an expiration time for an order book and reusing it before the deadline.
# Set it to 0 (always refresh) if the main thread already sleeps long enough
# between rounds.
refresh_time_sec = 0
# The timeout of the API operations.
timeout_sec = 20

# Commissions, as a rate of the trading volume.  Volume discounts are not
# considered.
#     https://www.bitstamp.net/fee_schedule/
#     https://btc-e.com/page/2
#     https://campbx.com/faq.php#trading
#     https://mtgox.com/fee-schedule
bitstamp_rate = 0.5/100
btce_rate = 0.2/100
compbx_rate = 0.55/100
mtgox_rate = 0.6/100

# The profit rate is defined by (sell - buy - commission) / buy.
# When 'sell' and 'buy' are sufficiently close, this is approximated to
# (sell - buy) / buy - (cr(A) + cr(B)), where cr(X) is the commision rate
# of exchange 'X'.  (The second formula is what is used by this program.)
# The marginal profit rate is defined as the profit rate of the last satoshi
# in the trade.
#
# The marginal profit rate varies among three values (low, normal, high),
# depending on the cash/bitcoin ratio in the involved exchanges.  The reason
# for this is because cash and bitcoins cannot be instantly transferred
# among exchanges, so the system must rebalance itself in the arbitrage
# transactions.  Initially, all the participating exchanges have about
# 50/50 cash and bitcoins, and 'marginal_profit_rate_normal' is used as the
# threshold for arbitrage transactions.  If an exchange becomes short on
# cash (defined by 'asset_ratio_low'), then it will use
# 'marginal_profit_rate_high' as the threshold for buying in this market, and
# 'marginal_profit_rate_low' as the threshold for selling in this market,
# so that the cash amount can be recovered.  Similarly, if an exchange becomes
# short on bitcoin (also defined by 'asset_ratio_low', it will use
# 'marginal_profit_rate_low' for buying and 'marginal_profit_rate_high' for
# selling.
marginal_profit_rate_low = 1.0/100
marginal_profit_rate_normal = 2.0/100
marginal_profit_rate_high = 3.0/100

# The dollar value of the minority asset divided by the dollar value of the
# majority asset in an exchange.
#
# TODO: The current model is rather simplified.  If there is a need, can use
#       a better data structure for this, eg:
#           { 0.25: (0.04, 0.02), 0.75: (0.02, 0.04) }
#       Ie, mapping an asset ratio to the buying and selling rates.
asset_ratio_low = 0.25

# Sometimes the order book fetched from an exchange contains matching orders
# (min ask price <= max bid price).  This may be due to server lags.
# For safety, turn on this flag to skip such order books in the arbitrage.
skip_order_books_with_matching_orders = True

