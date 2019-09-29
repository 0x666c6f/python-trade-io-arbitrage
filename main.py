from TradeIO import trade_io

trade_io_instance = trade_io.TradeIO()
res = trade_io_instance.order("eth_btc","limit","sell",99999999,0.01)
order = res['order']['orderId']
print(order)
res2 = trade_io_instance.cancel_order(order)