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


def btc_eth_arbitrage(tickers, infos, symbol, trade_io):
    try:
        ticker_btc = tickers[symbol+"_btc"]
        ticker_eth = tickers[symbol+"_eth"]
        ticker_eth_btc = tickers["eth_btc"]
    except KeyError:
        return
    try:
        prec_btc = infos[symbol + "_btc"]['baseAssetPrecision']
        prec_eth = infos[symbol + "_eth"]['baseAssetPrecision']
        prec_eth_btc = infos["eth_btc"]['baseAssetPrecision']
    except KeyError:
        return

    ask_btc = ticker_btc['askPrice']
    ask_btc_qty = ticker_btc['askQty']
    bid_eth = ticker_eth['bidPrice']
    bid_eth_qty = ticker_eth['bidQty']
    ask_eth_btc = ticker_eth_btc['askPrice']
    bid_eth_btc = ticker_eth_btc['bidPrice']

    if ask_btc > 0 and ask_btc_qty > 0 and bid_eth > 0 and bid_eth_qty > 0 and bid_eth_btc > 0:
        bonus = bid_eth * bid_eth_btc / ask_btc
        price = ask_btc

        if bonus > TradeIO.MIN_BONUS:
            if (
                    ask_btc * ask_btc_qty > TradeIO.MIN_BTC and
                    bid_eth * bid_eth_qty > TradeIO.MIN_ETH and
                    bid_eth * bid_eth_qty * ask_eth_btc > TradeIO.MIN_BTC and
                    TradeIO.MAX_BTC / price > TradeIO.MIN_BTC
            ):
                qty = min([TradeIO.MAX_BTC/price, ask_btc_qty, bid_eth_qty])
                qty = math.floor(qty * 10**prec_btc) / float(10**prec_btc)

                if qty == 0:
                    return

                TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                TradeIO.TOTAL_ORDER_WEIGHT += 1

                order_a_resp = trade_io.order(symbol + '_btc', 'limit', 'buy', price, qty)
                if order_a_resp['code'] == 0 and order_a_resp['order']['status'] == "Completed":
                    price = bid_eth
                    order_a_amount_filled = order_a_resp['order']['baseAmount']
                    order_a_commission = order_a_resp['order']['commission']
                    qty = math.floor((order_a_amount_filled-order_a_commission) * 10**prec_eth) / float(10**prec_eth)

                    TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                    TradeIO.TOTAL_ORDER_WEIGHT += 1

                    order_b_resp = trade_io.order(symbol+'_eth', 'limit', 'sell', price, qty)
                    if order_b_resp['code'] == 0 and order_b_resp['order']['status'] == "Completed":
                        price = bid_eth_btc
                        order_b_amount_filled = order_b_resp['order']['baseAmount']
                        order_b_commission = order_b_resp['order']['commission']
                        qty = math.floor((order_b_amount_filled - order_b_commission) * 10 ** prec_eth_btc) / float(10 ** prec_eth_btc)

                        TradeIO.TOTAL_GLOBAL_WEIGHT += 1
                        TradeIO.TOTAL_ORDER_WEIGHT += 1

                        order_c_resp = trade_io.order('eth_btc', 'limit', 'sell', price, qty)

                        logger.info("Successful Arbitrage result : <", symbol, ">", " bonus = ", bonus)
    else:
        return
    pass
