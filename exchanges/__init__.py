import json
import logging
from typing import Dict, List, Tuple
from exchanges.interface import Exchange, OHLCV
from exchanges.binance import Binance

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)


class Exchanges:
    def __init__(self):
        self.__exchanges: [Exchange] = [
            Binance(),
        ]
        # TODO: Make this an environment variable
        self.__supported_pairs = {'BTC', 'USDT'}

    # Exchange -> (Base, Quote) -> Prices
    def get_prices(self) -> Dict[str, Dict[Tuple[str, str], List[OHLCV]]]:
        ret = {}
        for exchange in self.__exchanges:
            supported_pairs = exchange.get_supported_assets()
            for pair in supported_pairs:
                if pair.normalized_base not in self.__supported_pairs or \
                        pair.normalized_quote not in self.__supported_pairs:
                    continue
                prices = exchange.get_last_hour_prices(pair.product_id)
                if isinstance(prices, List):
                    ret.setdefault(exchange.name(), {})
                    ret[exchange.name()][(pair.normalized_base, pair.normalized_quote)] = prices
        return ret


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path='../.env')
    logger.setLevel(logging.DEBUG)

    exchanges = Exchanges()
    prices_by_exchanges = exchanges.get_prices()
    for name, exchange_prices in prices_by_exchanges.items():
        print(name.ljust(10))
        for (base, quote), prices in exchange_prices.items():
            print(''.ljust(10) + f'{base}-{quote}'.ljust(10))
            print(prices)
