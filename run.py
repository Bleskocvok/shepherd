#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import ftplib

# my imports
from database import Database
from shepherd import ShepherdCog


'''
WEIRD FTP STUFF
(for deployment purposes)
'''
server = None
port = 21
username = 'anonymous'
password = 'anonymous'

def load(fname):
    try:
        with ftplib.FTP(server, username, password) as ftp:
            with open(fname, 'wb') as f:
                ftp.retrbinary('RETR ' + os.path.basename(fname), f.write)
    except Exception as e:
        print('Couldn\'t FTP load {}: '.format(fname, str(e)))


def save(fname):
    try:
        with ftplib.FTP(server, username, password) as ftp:
            with open(fname, 'rb') as f:
                ftp.storbinary('STOR ' + os.path.basename(fname), f)
    except Exception as e:
        print('Couldn\'t FTP save {}: '.format(fname, str(e)))


'''
MAIN
'''
# load Discord token from file and stuff
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
timezone = os.getenv('TIMEZONE_DIFF', 0)

timezone = int(timezone)
print('Using timezone difference of {}'.format(timezone))

# load ftp stuff
server = os.getenv('FTP_SERVER')
port = os.getenv('FTP_PORT', port)
username = os.getenv('FTP_USERNAME', username)
password = os.getenv('FTP_PASSWORD', password)

# start database in the data folder
# if ftp is activated add load and save routines
data = None
if server is None:
    data = Database('data')
else:
    print('Connecting to FTP: {}'.format(server))
    data = Database('data', load, save)

# start the client
client = commands.Bot(command_prefix='!')
client.add_cog(ShepherdCog(client, data, timezone))
client.run(token)

