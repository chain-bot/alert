import os
from typing import List
from dataclasses import dataclass


@dataclass
class CurrencyPair:
    product_id: str
    raw_base: str
    normalized_base: str
    raw_quote: str
    normalized_quote: str

    def __str__(self):
        spacing = 20
        header = "Product ID".ljust(spacing) +\
                 "Raw Base".ljust(spacing) +\
                 "Normalized Base".ljust(spacing) +\
                 "Quote".ljust(spacing) +\
                 "Normalized Quote".ljust(spacing)
        row = self.product_id.ljust(spacing) +\
            self.raw_base.ljust(spacing) +\
            self.normalized_base.ljust(spacing) +\
            self.raw_quote.ljust(spacing) +\
            self.normalized_quote.ljust(spacing)
        return f'{header}\n{row}'


@dataclass
class OHLCV:
    open: float
    high: float
    low: float
    close: float
    volume: float

    # Metadata
    time: int = 0.0
    granularity: int = 60


# TODO: Get Raw Trades (whale alerts?)
class Exchange:
    def __init__(self):
        fiat_currencies_raw: str = os.getenv('FIAT_CURRENCY') or 'CAD,USD'
        self.fiat = [fiat_currency.strip() for fiat_currency in fiat_currencies_raw.split(',')]

    def name(self) -> str:
        raise Exception('Interface Method')

    def get_supported_assets(self) -> List[CurrencyPair]:
        raise Exception('Interface Method')

    # TODO: Make this more robust
    def get_last_hour_prices(self, product_id: str) -> [OHLCV]:
        raise Exception('Interface Method')
