#!/usr/bin/env python3

import discord
import asyncio
from discord.ext import commands

# my imports
from database import Database
from scheduler import Scheduler


class MyCog(commands.Cog):
    messages = {
        'scheduled' : '```Scheduled exercise for {} in channel #{}```',
        'cancelled' : '```Cancelled scheduled exercise for channel {}```',
        'invalid_time' : '```Incorrect time format\nCorrect format is \'XX:XX\'```',
        'status' : '```Scheduled for {}:{}```',
        'not_status' : '```Not scheduled```',
        'stats' : '```{} | {}```',

        # was kinda difficult to find how to use emoji reactions
        'did_reaction' : '\N{FLEXED BICEPS}',
    }

    def __init__(self, bot, database : Database):
        self.bot = bot
        self.database = database
        self.scheduler = Scheduler()

    def job(self, ID):
        chn = self.bot.get_channel(ID)
        if chn is None:
            return
        # add zero for all current members
        for mem in chn.members:
            self.database.add_user_stats(mem.id, 0)
        # some coroutine hackery, so that this function (job) doesn't have to be async
        # notifies everyone for exercise!
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

    @commands.command(help='Shows current schedule')
    async def status(self, ctx):
        ID = ctx.message.channel.id
        found = self.database.get_channels().get(ID, None)
        if not found is None:
            h, m = found
            await ctx.send(MyCog.messages['status'].format(h, m))
        else:
            await ctx.send(MyCog.messages['not_status'])

    @commands.command(help='Stores the number of pushups you did', description='Current exercise session \
has to have been announced in order for your score to apply (otherwise it\'s applied to a previous session).')
    async def did(self, ctx, count : int):
        # set last value to count
        self.database.edit_last_stats(ctx.message.author.id, count)
        # add funny reaction :)
        requested = MyCog.messages['did_reaction']
        emoji = discord.utils.find(lambda x : requested in str(x), self.bot.emojis)
        await ctx.message.add_reaction(MyCog.messages['did_reaction'])

    @commands.command(help='Shows stats for a user')
    async def stats(self, ctx, username=''):
        if len(username) == 0:
            username = ctx.message.author.name
        id = discord.utils.get(ctx.message.channel.members, name=username).id
        result = self.database.get_user_stats(id)
        await ctx.send(MyCog.messages['stats'].format(username, result))

    @commands.command(help='Shows stats for all users in the current channel')
    async def allstats(self, ctx, username=''):
        result = '```'
        max_len = len(max(ctx.message.channel.members, key=lambda x : len(x.name)).name) + 1
        for mem in ctx.message.channel.members:
            data = self.database.get_user_stats(mem.id)
            result += '{} | {}'.format(mem.name.ljust(max_len), data) + '\n'
        result += '```'
        await ctx.send(result)

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

