import logging
from exchanges import Exchanges
import firestore
from exchanges.utils import get_largest_price
from slack import Slack
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('Starting coinprice-alert worker')

    exchanges = Exchanges()
    slack = Slack()

    for exchange_name, price_map in exchanges.get_prices().items():
        # base -> quote -> price
        stored_ath_data = firestore.get_ath_data(exchange_name)

        for (base, quote), prices in price_map.items():
            highest_price = get_largest_price(prices)
            if stored_ath_data is None or base not in stored_ath_data or quote not in stored_ath_data[base]:
                firestore.set_exchange_ath_data(exchange_name, base, quote, highest_price)
                slack.publish_init_message(exchange_name, base, quote, 0, highest_price)
            elif stored_ath_data[base][quote] < highest_price:
                firestore.set_exchange_ath_data(exchange_name, base, quote, highest_price)
                slack.publish_ath_message(exchange_name, base, quote, stored_ath_data[base][quote], highest_price)

    logger.info('Exiting coinprice-alert worker')
