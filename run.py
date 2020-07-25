#!/usr/bin/env python3

import discord
import asyncio
from discord.ext import commands

# my imports
from database import Database
from scheduler import Scheduler


class MyCog(commands.Cog):
    messages = {
        'scheduled' : '```Scheduled exercise for {} in channel {}```',
        'cancelled' : '```Cancelled scheduled exercise for channel {}```',
        'invalid_time' : '```Incorrect time format\nCorrect format is \'XX:XX\'```',
        'status' : '```Scheduled for {}:{}```',
        'not_status' : '```Not scheduled```',
    }

    def __init__(self, bot, database : Database):
        self.bot = bot
        self.database = database
        self.scheduler = Scheduler()

    def job(self, ID):
        chn = self.bot.get_channel(ID)
        if chn is None:
            return
        # some coroutine hackery, so that this function (job) doesn't have to be async
        future  = asyncio.run_coroutine_threadsafe(chn.send('@everyone Exercise time!'), self.loop)
        future.result()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Connected as {}'.format(self.bot.user.name))
        # add already scheduled notifs
        for ID, t in self.database.get_channels().items():
            self.scheduler.add(ID, t, self.job)
        self.scheduler.run()
        # load this thing (it's needed)
        self.loop = asyncio.get_event_loop()

    @commands.command(help='Schedules a time for exercise')
    async def schedule(self, ctx, time):
        time = time.strip()
        if time[len(time) - 1] == '\n':
            time = time[:len(time) - 1]
        if not self.correct_time(time):
            await ctx.send(MyCog.messages['invalid_time'])
            return
        t = (int(time[0:2]), int(time[3:5]))
        ID = ctx.message.channel.id
        self.database.set_channel(ID, t)
        self.scheduler.add(ID, t, self.job)
        await ctx.send(MyCog.messages['scheduled'].format(time, ctx.message.channel.name))

    @commands.command(help='Cancels scheduled exercise')
    async def cancel(self, ctx):
        ID = ctx.message.channel.id
        self.database.remove_channel(ID)
        self.scheduler.remove(ID)
        await ctx.send(MyCog.messages['cancelled'].format(ctx.message.channel.name))

    @commands.command(help='Prints current schedule')
    async def status(self, ctx):
        ID = ctx.message.channel.id
        found = self.database.get_channels().get(ID, None)
        if not found is None:
            h, m = found
            await ctx.send(MyCog.messages['status'].format(h, m))
        else:
            await ctx.send(MyCog.messages['not_status'])

    @commands.command(help='[To be done] Stores the number of pushups you did')
    async def did(self, ctx, count : int):
        pass

    @commands.command(help='[To be done]')
    async def stats(self, ctx, name):
        pass

    def correct_time(self, time):
        nums = '0123456789'
        if len(time) != 5 or time[2] != ':':
            return False
        if not time[0] in nums:
            return False
        if not time[1] in nums:
            return False
        if not time[3] in nums:
            return False
        if not time[4] in nums:
            return False
        return True

'''
MAIN
'''
# load Discord token from file 'secret_token.txt'
token = ''
with open('secret_token.txt', 'r') as f:
    token = f.read().strip()

# load saved data
data = Database('data')

# start the client
client = commands.Bot(command_prefix='!')
client.add_cog(MyCog(client, data))
client.run(token)

'''
@client.event
async def on_command_error(ctx, error):
    print(error)
'''
