import json
import logging
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlencode
import dateparser
import pytz
import requests
from backoff import on_exception, expo
from ratelimit import limits, RateLimitException
from exchanges.interface import Exchange, OHLCV, CurrencyPair

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

NAME = 'BINANCE'
BASE_URL = 'https://api.binance.com'
EXCHANGE_INFO = '/api/v3/exchangeInfo'
KLINES = '/api/v3/klines'
GET = 'GET'
ONE_MINUTE = 60
KLINE_LIMIT = 1000
ONE_HOUR_MILI = 60 * 60 * 1000

# TODO: Make this more robust
KLINE_INTERVAL = "1m"
KLINE_GRANULARITY = 60


# https://sammchardy.github.io/binance/2018/01/08/historical-data-download-binance.html
def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    d = d - timedelta(minutes=d.minute, seconds=d.second, microseconds=0)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)
    # return the difference in time
    return int((d - epoch).total_seconds()) * 1000


class Binance(Exchange):

    def __init__(self):
        super().__init__()
        logging.info(f"Initialized {self.name()} Exchange")

    def name(self) -> str:
        return NAME

    @on_exception(expo, RateLimitException, max_tries=10)
    @limits(calls=10, period=ONE_MINUTE)
    def get_supported_assets(self) -> List[CurrencyPair]:
        url = f'{BASE_URL}{EXCHANGE_INFO}'
        r = requests.get(url)
        traded_pairs = r.json()['symbols']

        ret = []
        for pair in traded_pairs:
            product_id = pair['symbol']
            base = pair['baseAsset']
            normalized_base = base.upper()
            quote = pair['quoteAsset']
            normalized_quote = quote.upper()
            ret.append(CurrencyPair(product_id, base, normalized_base, quote, normalized_quote))
        return ret

    @on_exception(expo, RateLimitException, max_tries=10)
    @limits(calls=10, period=ONE_MINUTE)
    def get_last_hour_prices(self, product_id: str) -> [OHLCV]:
        end_time = date_to_milliseconds("now UTC")
        start_time = end_time - ONE_HOUR_MILI
        params = {
            'symbol': product_id,
            'interval': KLINE_INTERVAL,
            'startTime': start_time,
            'endTime': end_time,
            'limit': KLINE_LIMIT
        }
        url = f'{BASE_URL}{KLINES}?{urlencode(params)}'
        r = requests.get(url)
        candles = r.json()
        ret = []
        for candle in candles:
            open_time = int(candle[0]) // 1000
            open_price = float(candle[1])
            high_price = float(candle[2])
            low_price = float(candle[3])
            close_price = float(candle[4])
            volume = float(candle[5])
            granularity = KLINE_GRANULARITY
            ret.append(OHLCV(open_price, high_price, low_price, close_price, volume, open_time, granularity))
        return ret


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path='../../.env')
    logger.setLevel(logging.DEBUG)

    exchange = Binance()
    currency_pairs = exchange.get_supported_assets()
    _ = {print(pair) for pair in currency_pairs}
    prices = exchange.get_last_hour_prices('BTCUSDT')
    _ = {print(ohlcv) for ohlcv in prices}
