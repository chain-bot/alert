# !/usr/bin/env python3

import requests
import json
import discord
from discord.ext import commands
from discord_slash import SlashCommand, cog_ext
from discord_slash import SlashContext
from constant import *


class SlashCommandCog(commands.Cog):
    def __init__(self, bot):
        if not hasattr(bot, "slash"):
            # Creates new SlashCommand instance to bot if bot doesn't have.
            bot.slash = SlashCommand(bot, override_type=True)
        self.bot = bot
        self.bot.slash.get_cog_commands(self)
        self.firestore_client = FIRESTORE_CLIENT
        self.delete_slash_commands()
        self.create_slash_commands()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'COG {self.__class__.__name__} Logged in as {self.bot.user.name} {self.bot.user.id}')
        print(PRINT_LINE)

    def cog_unload(self):
        self.bot.slash.remove_cog_commands(self)

    @staticmethod
    def create_slash_commands(debug=True):
        if debug:
            create_slash_command_url = f"{DISCORD_API_BASE_URL}/{APPLICATION_ID}/guilds/{DEBUG_GUILD_ID}/commands"
        else:
            create_slash_command_url = f"{DISCORD_API_BASE_URL}/{APPLICATION_ID}/commands"
        with open('slash_commands.json') as f:
            slash_commands = json.load(f)
            print(f'CREATING {len(slash_commands)} SLASH COMMANDS')
            for command in slash_commands:
                r = requests.post(create_slash_command_url, headers=HEADERS, json=command)
                print(f'CREATING "{command["name"]}" SLASH COMMAND {r.status_code}')
        print(PRINT_LINE)

    @staticmethod
    def delete_slash_commands(debug=True):
        if debug:
            list_slash_commands_url = f"{DISCORD_API_BASE_URL}/{APPLICATION_ID}/guilds/{DEBUG_GUILD_ID}/commands"
        else:
            list_slash_commands_url = f"{DISCORD_API_BASE_URL}/{APPLICATION_ID}/commands"
        r = requests.get(list_slash_commands_url, headers=HEADERS)
        slash_commands = json.loads(r.content)
        print(f'DELETING {len(slash_commands)} SLASH COMMANDS')
        for command in slash_commands:
            if debug:
                delete_slash_command_url = f"{DISCORD_API_BASE_URL}/{APPLICATION_ID}/guilds/{DEBUG_GUILD_ID}/commands/{command['id']}"
            else:
                delete_slash_command_url = f"{DISCORD_API_BASE_URL}/{APPLICATION_ID}/commands/{command['id']}"
            response = requests.delete(delete_slash_command_url, headers=HEADERS)
            print(f'DELETING SLASH COMMAND {response.status_code}')
        print(PRINT_LINE)

    @cog_ext.cog_slash(name="price")
    async def _price(self, ctx: SlashContext, *options):
        base = options[0].upper()
        quote = options[1].upper() if len(options) > 1 else "USDT"
        if base == quote:
            print("BASE AND QUOTE MUST BE DIFFERENT")
            await ctx.send(content='😠 "Base" and "Quote" symbols must be different!')
        else:
            binance_price_url = f"https://api.binance.com/api/v3/klines?symbol={base + quote}&interval=1m&limit=1"
            r = requests.get(binance_price_url)
            price = json.loads(r.content)
            content = f"{base}/{quote}"
            embed_open = discord.Embed(title=f"OPEN: {price[0][1]}")
            embed_high = discord.Embed(title=f"HIGH: {price[0][2]}")
            embed_low = discord.Embed(title=f"LOW: {price[0][3]}")
            embed_close = discord.Embed(title=f"CLOSE: {price[0][4]}")
            await ctx.send(content=content, embeds=[embed_open, embed_high, embed_low, embed_close])
            print(f'SUCCESSFULLY GOT PRICE FOR {base}/{quote}')
        print(PRINT_LINE)

    @cog_ext.cog_slash(name="register_ath_alert")
    async def _register_ath_alert(self, ctx: SlashContext):
        doc_ref = self.firestore_client.collection("ATH").document(f'registered')
        doc_ref.set({f'{ctx.channel.id}': True}, merge=True)
        print(f'REGISTERED SUCCESSFULLY')
        print(PRINT_LINE)
        await ctx.send(content=f"Successfully registered channel {ctx.channel} for ATH alerts.")

    @cog_ext.cog_slash(name="unregister_ath_alert")
    async def _unregister_ath_alert(self, ctx: SlashContext):
        doc_ref = self.firestore_client.collection("ATH").document(f'registered')
        doc_ref.update({f'{ctx.channel.id}': False})
        print(f'UNREGISTERED SUCCESSFULLY')
        print(PRINT_LINE)
        await ctx.send(content=f"Successfully unregistered channel {ctx.channel} from ATH alerts.")


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(SlashCommandCog(bot))
