import math

from TradeIO.trade_io import TradeIO
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def ethbtc_usdtbtc_ethbtc_arbitrage(tickers, infos, symbol, source, intermediate, trade_io):
    try:
        ticker_source = tickers[symbol + "_" + source]
        ticker_intermediate = tickers[symbol + "_" + intermediate]
        ticker_source_intermediate = tickers[source + "_" + intermediate]

    except KeyError:
        return
    try:
        prec_source = infos[symbol + '_'+ source]['baseAssetPrecision']
        prec_intermediate = infos[symbol + "_" + intermediate]['baseAssetPrecision']
        prec_source_intermediate = infos[source + '_'+intermediate]['baseAssetPrecision']
    except KeyError:
        return

    if intermediate == "eth":
        min_intermediate = TradeIO.MIN_ETH
    else:
        min_intermediate = TradeIO.MIN_BTC

    ask_source = ticker_source['askPrice']
    ask_source_qty = ticker_source['askQty']
    bid_intermediate = ticker_intermediate['bidPrice']
    bid_intermediate_qty = ticker_intermediate['bidQty']
    ask_source_intermediate = ticker_source_intermediate['askPrice']
    bid_source_intermediate = ticker_source_intermediate['bidPrice']

    if ask_source > 0 and ask_source_qty > 0 and bid_intermediate > 0 and bid_intermediate_qty > 0 and ask_source_intermediate > 0 and bid_source_intermediate > 0:
        bonus = bid_intermediate / ask_source / ask_source_intermediate
        price = ask_source

        if bonus > TradeIO.MIN_BONUS:

            if intermediate == "eth":
                min_intermediate = TradeIO.MIN_ETH
            elif intermediate == "btc":
                min_intermediate = TradeIO.MIN_BTC
            else:
                min_intermediate = TradeIO.MIN_USDT

            if source == "eth":
                min_source = TradeIO.MIN_ETH
                max_source = TradeIO.MAX_ETH
            elif source == "btc":
                min_source = TradeIO.MIN_BTC
                max_source = TradeIO.MAX_BTC
            else:
                min_source = TradeIO.MIN_USDT
                max_source = TradeIO.MAX_USDT

            if (
                    bid_intermediate * bid_intermediate_qty > min_intermediate and
                    ask_source * ask_source_qty > min_source and
                    ask_source * ask_source_qty * ask_source_intermediate > min_intermediate and
                    max_source / price > min_source
            ):
                qty = min([max_source / price, ask_source_qty, bid_intermediate_qty])
                qty = math.floor(qty * 10 ** prec_source) / float(10 ** prec_source)

                if qty == 0:
                    return

                TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                TradeIO.TOTAL_ORDER_WEIGHT += 1

                order_a_resp = trade_io.order(symbol + '_' + source, 'limit', 'buy', price, qty)
                if order_a_resp['code'] == 0 and order_a_resp['order']['status'] == "Completed":
                    price = bid_intermediate
                    order_a_amount_filled = order_a_resp['order']['baseAmount']
                    order_a_commission = order_a_resp['order']['commission']
                    qty = math.floor((order_a_amount_filled - order_a_commission) * 10 ** prec_intermediate) / float(
                        10 ** prec_intermediate)

                    TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                    TradeIO.TOTAL_ORDER_WEIGHT += 1

                    order_b_resp = trade_io.order(symbol + '_' + intermediate, 'limit', 'sell', price, qty)
                    if order_b_resp['code'] == 0 and order_b_resp['order']['status'] == "Completed":
                        price = ask_source_intermediate
                        order_b_amount_filled = order_b_resp['order']['baseAmount']
                        order_b_commission = order_b_resp['order']['commission']
                        qty = math.floor(
                            (order_b_amount_filled - order_b_commission)/price * 10 ** prec_source_intermediate) / float(
                            10 ** prec_source_intermediate)

                        TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                        TradeIO.TOTAL_ORDER_WEIGHT += 1

                        order_c_resp = trade_io.order(source + '_' + intermediate, 'limit', 'buy', price, qty)

                        logger.info("Successful Arbitrage result : <", symbol, ">", " bonus = ", bonus)
    else:
        return
