#!/usr/bin/env python3

import discord
from discord.ext import commands

# my imports
from database import Database
from shepherd import ShepherdCog


'''
MAIN
'''
# load Discord token from file 'secret_token.txt'
token = ''
with open('secret_token.txt', 'r') as f:
    token = f.read().strip()

# start database in the data folder
data = Database('data')

# start the client
client = commands.Bot(command_prefix='!')
client.add_cog(ShepherdCog(client, data))
client.run(token)

