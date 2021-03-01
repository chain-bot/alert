import json
import logging
import os
import sys
import requests
logger = logging.getLogger(__name__)


def _get_ath_mesage_block(exchange, base, quote, old_price, new_price):
    message = exchange.ljust(20) +\
              f'{base}-{quote}'.ljust(10) +\
              str(old_price).ljust(20) +\
              "->".ljust(5) +\
              str(new_price).ljust(20)
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": message
        }
    }


class Slack:
    def __init__(self):
        self.__webhook = os.getenv('SLACK_WEBHOOK')
        if self.__webhook is None:
            logger.error('FORGOT SLACK WEBHOOK')
            sys.exit()

    def _send_message(self, title, message_blocks):
        logger.debug("Sending Message")
        r = requests.post(self.__webhook,
                          data=json.dumps({"text": title, "blocks": message_blocks}),
                          headers={'Content-Type': 'application/json'}, verify=True)
        logger.debug(r.status_code)
        logger.debug(r.text)
        logger.debug("Message Sent")

    def publish_ath_message(self, exchange, base, quote, old_price, new_price):
        self._send_message(f"New All Time High for {base}-{quote}", [
            _get_ath_mesage_block(exchange, base, quote, old_price, new_price)])

    def publish_init_message(self, exchange, base, quote, old_price, new_price):
        print("Sending init message")
        message_blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"This is the first alert for {base}-{quote}. If the data is wrong, please update it in the "
                        f"firestore console. "
            }
        }, _get_ath_mesage_block(exchange, base, quote, old_price, new_price)]
        self._send_message(f"New All Time High for {base}-{quote}", message_blocks)
