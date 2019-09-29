import requests 
import logging
import hashlib
import hmac
import json
import time

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TradeIO:
    endpoint = 'https://api.exchange.trade.io'
    key = '8bbcf739-e5f9-46df-8a07-884aeaa9e7d1'
    secret = '100ad32f-5e7b-4a37-8c7f-e1199d1943db'

    def __init__(self):
        pass
    
    def sign(self,args):
        data = ''

        if type(args) == dict:
            data = json.dumps(args).encode('utf-8')
        else:
            data = args.encode('utf-8')

        return hmac.new(TradeIO.secret.encode('utf-8'), data, hashlib.sha512).hexdigest()

    def info(self):
        data = ''
        res=''

        try:
            res = requests.get(url = TradeIO.endpoint+'/api/v1/info') 
            # extracting data in json format 
            data = res.json() 
        except:
            logger.error(f'Error  retrieving infos: {res}')
        return data

    def tickers(self):
        data = ''
        res=''
        try:
            res = requests.get(url = TradeIO.endpoint+'/api/v1/tickers') 
            # extracting data in json format 
            data = res.json() 
            logger.info(data)
        except:
            logger.error(msg=f'Error  retrieving tickers: {res}')
        return data

    def order(self, symbol, order_type, side, price, qty):
        data = ''
        res=''
        try:
            order = {
                'Symbol': symbol,
                'Side': side,
                'Type': order_type,
                'Quantity': qty,
                'Price': price,
                'ts': int(round(time.time() * 1000)),
            }
            headers = {
                'Key': TradeIO.key,
                'Sign': self.sign(order).upper(),
                'Content-Type': 'application/json'
            }

            res = requests.post(url = TradeIO.endpoint+'/api/v1/order', data = json.dumps(order), headers=headers) 
            data = res.json()
            logger.info(data)
        except:
            logger.error('Error creating order:')
            raise
        return data

    def cancel_order(self, order_id):
        data = ''
        res=''
        try:
            ts = '?ts='+str(int(round(time.time() * 1000)))
            headers = {
                'Key': TradeIO.key,
                'Sign': self.sign(ts).upper(),
                'Content-Type': 'application/json'
            }

            res = requests.delete(url = TradeIO.endpoint+'/api/v1/order/'+order_id+ts, headers=headers) 
            data = res.json()
            logger.info(data)
        except:
            logger.error('Error deleting order:')
            raise
        return data

    def balance(self):
        data = ''
        res=''
        try:
            ts = '?ts='+str(int(round(time.time() * 1000)))
            headers = {
                'Key': TradeIO.key,
                'Sign': self.sign(ts).upper(),
                'Content-Type': 'application/json'
            }

            res = requests.get(url = TradeIO.endpoint+'/api/v1/account'+ts, headers=headers) 
            data = res.json()
            logger.info(data)
        except:
            logger.error('Error getting balance:')
            raise
        return data