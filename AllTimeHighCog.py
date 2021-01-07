# !/usr/bin/env python3
import requests
import json
import discord
from discord.ext import tasks, commands
from typing import Dict, List
import traceback
from constant import *


class AllTimeHighCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.firestore_client = FIRESTORE_CLIENT

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'COG {self.__class__.__name__} Logged in as {self.bot.user.name} {self.bot.user.id}')
        print(PRINT_LINE)
        self.send_all_time_high_message.start()

    @tasks.loop(seconds=120.0)
    async def send_all_time_high_message(self):
        print("CHECKING ALL TIME HIGHS")
        channel_ids = self.find_registered_channels()
        all_time_highs = self.check_all_time_highs()
        for channel_id in channel_ids.keys():
            for all_time_high in all_time_highs:
                channel = await self.bot.fetch_channel(int(channel_id))
                await channel.send(all_time_high)
        print(PRINT_LINE)

    def find_registered_channels(self) -> Dict[str, bool]:
        channel_doc = self.firestore_client.collection("ATH").document(f'registered').get()
        channel_ids = {key: value for key, value in channel_doc.to_dict().items() if value}
        return channel_ids

    def check_all_time_highs(self) -> List[str]:
        ret = []
        for base_symbol in ["BTC", "ETH"]:
            price_updates = {}
            doc_ref = self.firestore_client.collection("ATH").document(f'{base_symbol}')
            for quote_symbol in ["BTC", "USDT"]:
                if base_symbol == quote_symbol:
                    continue
                binance_price_url = f"{BINANCE_BASE_URL}/klines?symbol={base_symbol + quote_symbol}&interval=1m&limit=1"
                try:
                    r = requests.get(binance_price_url)
                    price = json.loads(r.content)
                    current_close = price[0][4]
                    price_updates[quote_symbol] = current_close
                    data = doc_ref.get().to_dict()
                    if data is None:
                        doc_ref.set({})
                        data = {}
                    last_checked_close = float(data.get(quote_symbol, 0))
                    if float(current_close) > last_checked_close:
                        ret.append(f'New ATH: {base_symbol}/{quote_symbol} {current_close}')
                        doc_ref.update({quote_symbol: current_close})
                except:
                    print("Error Getting Price Data from Binance")
                    traceback.print_exc()
                    print(PRINT_LINE)
        return ret


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(AllTimeHighCog(bot))
