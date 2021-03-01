# !/usr/bin/env python3

from discord.ext import commands
from constant import *
bot = commands.Bot(command_prefix="!")
for extension in ['SlashCommandCog', 'AllTimeHighCog']:
    bot.load_extension(extension)
bot.run(TOKEN)
