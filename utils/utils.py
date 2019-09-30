class Utils:
    def format_balance(self,raw_balance):
        return {b['asset']:b for b in raw_balance['balances']}

    def format_infos(self,raw_infos):
        return {i['symbol']:i for i in raw_infos['symbols']}

    def format_tickers(self,raw_tickers):
        return {t['symbol']:t for t in raw_tickers['tickers']}