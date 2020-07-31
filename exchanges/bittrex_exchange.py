from bittrex.bittrex import Bittrex, API_V1_1, API_V2_0
from expiringdict import ExpiringDict

from config import bot_cfg, log


class BittrexExchange:
    def __init__(self):
        self.disabled = False

        api_key = bot_cfg("BTREX_KEY")
        api_secret = bot_cfg("BTREX_SECRET")

        if api_key is None or api_secret is None:
            self.disabled = True
            log.info(
                "Disable BITTREX because either api_key or api_secret not available"
            )
        else:
            self.bittrex_v1 = Bittrex(api_key, api_secret, api_version=API_V1_1)
            self.bittrex_v2 = Bittrex(api_key, api_secret, api_version=API_V2_0)
            self.cache = ExpiringDict(max_len=200, max_age_seconds=60)

    def is_disabled(self):
        return self.disabled

    def name(self):
        return self.__class__.__name__

    def get_open_orders(self):
        log.info("{}: Getting open orders".format(self.name()))

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        if self.cache.get("open_orders"):
            return self.cache.get("open_orders")

        open_orders_response = self.bittrex_v1.get_open_orders()

        open_orders = self.result(open_orders_response)
        self.cache["open_orders"] = open_orders
        return open_orders

    def get_orders_history(self):
        log.info("{}: Getting order history".format(self.name()))

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        if self.cache.get("order_history"):
            return self.cache.get("order_history")

        order_history_response = self.bittrex_v1.get_order_history()

        order_history = self.result(order_history_response)
        self.cache["order_history"] = order_history
        return order_history

    def get_price(self, symbol):
        log.info("{}: Getting ticker data for {}".format(self.name(), symbol))

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        if self.cache.get(symbol):
            return self.cache.get(symbol)

        ticker_info_response = self.bittrex_v1.get_ticker(symbol)

        ticker_info = self.result(ticker_info_response)
        self.cache[symbol] = ticker_info
        return ticker_info

    def trade_commission(self, quantity, price):
        trade_value = float(quantity) * float(price)
        exchange_commission = trade_value * 0.0025
        return trade_value, exchange_commission, trade_value + exchange_commission

    def get_market_summaries(self):
        log.info("{}: Getting market summaries from exchange".format(self.name()))

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        if self.cache.get("market_summaries_api"):
            return self.cache.get("market_summaries_api")

        market_summaries_api_response = self.bittrex_v1.get_market_summaries()

        market_summaries_api = self.result(market_summaries_api_response)
        self.cache["market_summaries_api"] = market_summaries_api
        return market_summaries_api

    def sell_order(self, quantity_to_sell, trade_symbol, sell_price):
        log.info(
            "{}: Selling {} (quantity) of {} (symbol) for {:06.8f} (price)".format(
                self.name(), quantity_to_sell, trade_symbol, sell_price
            )
        )

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        sell_limit_response = self.bittrex_v2.trade_sell(
            market=trade_symbol,
            order_type="LIMIT",
            quantity=quantity_to_sell,
            rate=sell_price,
            time_in_effect="GOOD_TIL_CANCELLED",
            condition_type="LESS_THAN",
            target=sell_price,
        )

        sell_limit = self.result(sell_limit_response)
        order_id = sell_limit.get("OrderId")

        return order_id

    def buy_order(self, quantity_to_buy, trade_symbol, buy_price):
        log.info(
            "{}: Buying {} (quantity) of {} (symbol) for {:06.8f} (price)".format(
                self.name(), quantity_to_buy, trade_symbol, buy_price
            )
        )

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        buy_limit_response = self.bittrex_v2.trade_buy(
            market=trade_symbol,
            order_type="LIMIT",
            quantity=quantity_to_buy,
            rate=buy_price,
            time_in_effect="GOOD_TIL_CANCELLED",
            condition_type="GREATER_THAN",
            target=buy_price,
        )

        buy_limit = self.result(buy_limit_response)
        order_id = buy_limit.get("OrderId")

        return order_id

    def get_balances(self):
        log.info("{}: Printing balance in exchange".format(self.name()))

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        if self.cache.get("balances"):
            return self.cache.get("balances")

        get_balances_response = self.bittrex_v1.get_balances()

        balances = [
            {
                "exchange": "BITTREX",
                "currency": b.get("Currency"),
                "available": b.get("Balance"),
            }
            for b in self.result(get_balances_response)
            if b.get("Balance") > 0
        ]
        self.cache["balances"] = balances
        return balances

    def track_order(self, order_id):
        log.info("{}: Tracking order: {}".format(self.name(), order_id))

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        get_order_response = self.bittrex_v2.get_order(order_id)

        order = self.result(get_order_response)
        quantity = order.get("Quantity")
        quantity_remaining = order.get("QuantityRemaining")
        settled = not order.get("IsOpen")
        status = "closed" if settled else "open"
        side = "sell" if order.get("Type") == "LIMIT_SELL" else "buy"
        price = float(order.get("Price"))
        limit = float(order.get("Limit"))
        commission_paid = float(order.get("CommissionPaid"))
        executed_value = price + commission_paid

        return {
            "id": order.get("OrderUuid"),
            "settled": settled,
            "side": side,
            "done_reason": "canceled" if quantity_remaining and settled else "done",
            "status": status,
            "price": price,
            "limit": "{:06.8f}".format(limit),
            "fill_fees": "{:06.8f}".format(commission_paid),
            "filled_size": quantity - quantity_remaining,
            "executed_value": "{:06.8f}".format(executed_value),
            "done_at": order.get("Closed"),
        }

    def cancel_order(self, order_id, reason=None):
        log.info(
            "{}: Cancelling order: {}, Reason: {}".format(self.name(), order_id, reason)
        )

        if self.is_disabled():
            raise EnvironmentError("{} is disabled".format(self.name()))

        cancelled_order_response = self.bittrex_v2.cancel(order_id)

        return self.result(cancelled_order_response)

    @staticmethod
    def result(api_response):
        if api_response.get("success"):
            return api_response.get("result")

        raise ConnectionError("API Failed: {}".format(api_response))
