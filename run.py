#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# my imports
from database import Database
from shepherd import ShepherdCog


'''
MAIN
'''
# load Discord token from file and stuff
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
timezone = os.getenv('TIMEZONE_DIFF', 0)

timezone = int(timezone)
print('Using timezone difference of {}'.format(timezone))

# start database in the data folder
data = Database('data')

# start the client
client = commands.Bot(command_prefix='!')
client.add_cog(ShepherdCog(client, data, timezone))
client.run(token)

