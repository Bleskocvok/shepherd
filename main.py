#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime

# my imports
from database import Database
from scheduler import Scheduler
from shepherd import ShepherdCog


'''
MAIN
'''

def main():
    # load Discord token from file and stuff
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    timezone = os.getenv('TIMEZONE_DIFF', 0)

    timezone = int(timezone)
    print('Current time:', datetime.datetime.now())
    print('Using timezone difference of {}'.format(timezone), flush=True)

    # start database in the data folder
    data = Database('data')
    sched = Scheduler(timezone)

    # turn on intents to acess channel.members (important)
    intents = discord.Intents.default()
    intents.members = True
    # start the client
    client = commands.Bot(command_prefix='!', intents=intents)
    client.add_cog(ShepherdCog(client, data, sched))
    client.run(token)


if __name__ == "__main__":
    main()


