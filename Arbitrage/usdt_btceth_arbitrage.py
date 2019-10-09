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


def usdt_btceth_arbitrage(tickers, infos, symbol, intermediate, trade_io):
    try:
        ticker_usdt = tickers[symbol+"_usdt"]
        ticker_intermediate = tickers[symbol+"_"+intermediate]
        ticker_intermediate_usdt = tickers[intermediate+'_usdt']
    except KeyError:
        return
    try:
        prec_usdt = infos[symbol + "_usdt"]['baseAssetPrecision']
        prec_intermediate = infos[symbol+"_"+intermediate]['baseAssetPrecision']
        prec_intermediate_usdt = infos[intermediate+'_usdt']['baseAssetPrecision']
    except KeyError:
        return

    if intermediate == "eth":
        minIntermediate = TradeIO.MIN_ETH
    else:
        minIntermediate = TradeIO.MIN_BTC

    ask_usdt = ticker_usdt['askPrice']
    ask_usdt_qty = ticker_usdt['askQty']
    bid_intermediate = ticker_intermediate['bidPrice']
    bid_intermediate_qty = ticker_intermediate['bidQty']
    ask_intermediate_usdt = ticker_intermediate_usdt['askPrice']
    bid_intermediate_usdt = ticker_intermediate_usdt['bidPrice']

    if ask_usdt > 0 and ask_usdt_qty > 0 and bid_intermediate > 0 and bid_intermediate_qty > 0 and bid_intermediate_usdt > 0:
        bonus = bid_intermediate_usdt * bid_intermediate / ask_usdt
        price = ask_usdt

        if bonus > TradeIO.MIN_BONUS:
            if (
                    ask_usdt * ask_usdt_qty > TradeIO.MIN_USDT and
                    bid_intermediate * bid_intermediate_qty > minIntermediate and
                    bid_intermediate * bid_intermediate_qty * ask_intermediate_usdt > TradeIO.MIN_USDT and
                    TradeIO.MAX_USDT / price > TradeIO.MIN_USDT
            ):
                qty = min([TradeIO.MAX_USDT/price, ask_usdt_qty, bid_intermediate_qty])
                qty = math.floor(qty * 10**prec_usdt) / float(10**prec_usdt)

                if qty == 0:
                    return

                TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                TradeIO.TOTAL_ORDER_WEIGHT += 1

                order_a_resp = trade_io.order(symbol + '_usdt', 'limit', 'buy', price, qty)
                if order_a_resp['code'] == 0 and order_a_resp['order']['status'] == "Completed":
                    price = bid_intermediate
                    order_a_amount_filled = order_a_resp['order']['baseAmount']
                    order_a_commission = order_a_resp['order']['commission']
                    qty = math.floor((order_a_amount_filled-order_a_commission) * 10**prec_intermediate) / float(10**prec_intermediate)

                    TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                    TradeIO.TOTAL_ORDER_WEIGHT += 1

                    order_b_resp = trade_io.order(symbol+'_'+intermediate, 'limit', 'sell', price, qty)
                    if order_b_resp['code'] == 0 and order_b_resp['order']['status'] == "Completed":
                        price = bid_intermediate_usdt
                        order_b_amount_filled = order_b_resp['order']['baseAmount']
                        order_b_commission = order_b_resp['order']['commission']
                        qty = math.floor((order_b_amount_filled - order_b_commission) * 10 ** prec_intermediate_usdt) / float(10 ** prec_intermediate_usdt)

                        TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                        TradeIO.TOTAL_ORDER_WEIGHT += 1

                        order_c_resp = trade_io.order(intermediate+'_usdt', 'limit', 'sell', price, qty)

                        logger.info("Successful Arbitrage result : <", symbol, ">", " bonus = ", bonus)
    else:
        return
