
import discord
import asyncio
from discord.ext import commands
from typing import Optional, List

# my imports
from database import Database
from scheduler import Scheduler


class ShepherdCog(commands.Cog):
    StatsMax = 7
    Messages = {
        'scheduled' : '```Scheduled exercise for {} in channel #{}```',
        'cancelled' : '```Cancelled scheduled exercise for channel {}```',
        'invalid_time' : '```Incorrect time format\nCorrect format is \'XX:XX\'```',
        'status' : '```Scheduled for {}:{}\nTime: {}```',
        'not_status' : '```Not scheduled```',
        # 'stats' : '```{} | {}```',
        'buff' : '\
{0}===={1}==={1}===={0}\n\
                 {2}{3}{2}\n'.format(
            '\N{WHITE LARGE SQUARE}',
            '\N{RAISED FIST}',
            '\N{FLEXED BICEPS}',
            '\N{SMILING FACE WITH SUNGLASSES}'),

        # was kinda difficult to find how to use emoji reactions
        'did_reaction' : '\N{FLEXED BICEPS}',
    }

    def __init__(self,
            bot,
            database : Database,
            scheduler : Scheduler):
        self.bot = bot
        self.database = database
        self.scheduler = scheduler

    def job(self, ID):
        chn = self.bot.get_channel(ID)
        if chn is None:
            return
        # add zero for all current members
        for mem in chn.members:
            self.database.add_user_stats(mem.id, ID, 0)
        # some coroutine hackery, so that this function (job) doesn't have to be async
        # notifies everyone for exercise!
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        future  = asyncio.run_coroutine_threadsafe(chn.send('@everyone Exercise time!'), self.loop)
        future.result()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print('ERROR:', error)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Connected as {}'.format(self.bot.user.name), flush=True)
        # add already scheduled notifs
        for ID, t in self.database.get_channels().items():
            self.scheduler.add(ID, t, self.job)
        self.scheduler.run()
        # load this thing (it's needed)
        self.loop = asyncio.get_event_loop()

    @commands.command(help='')
    async def buff(self, ctx):
        await ctx.send('{0}===={1}==={1}===={0}\n\
                 {2} {3} {2}\n'.format(
            '\N{WHITE LARGE SQUARE}',
            '\N{RAISED FIST}',
            '\N{FLEXED BICEPS}',
            '\N{SMILING FACE WITH SUNGLASSES}'))

    @commands.command(help='Prints current time')
    async def time(self, ctx):
        await ctx.send('```{}```'.format(self.scheduler.get_time()))

    @commands.command(help='Schedules a time for exercise')
    async def schedule(self, ctx, time):
        time = time.strip()
        if time[len(time) - 1] == '\n':
            time = time[:len(time) - 1]
        if not self.correct_time(time):
            await ctx.send(ShepherdCog.Messages['invalid_time'])
            return
        t = (int(time[0:2]), int(time[3:5]))
        # message first, save to database later (might be slow)
        await ctx.send(ShepherdCog.Messages['scheduled']
                .format(time, ctx.message.channel.name))
        ID = ctx.message.channel.id
        self.database.set_channel(ID, t)
        self.scheduler.add(ID, t, self.job)

    @commands.command(help='Cancels scheduled exercise')
    async def cancel(self, ctx):
        # message first, save to database later (might be slow)
        await ctx.send(ShepherdCog.Messages['cancelled']
                .format(ctx.message.channel.name))
        ID = ctx.message.channel.id
        self.database.remove_channel(ID)
        self.scheduler.remove(ID)

    @commands.command(help='Shows current schedule')
    async def status(self, ctx):
        ID = ctx.message.channel.id
        found = self.database.get_channels().get(ID, None)
        if not found is None:
            h, m = found
            await ctx.send(ShepherdCog.Messages['status']
                    .format(h, m, str(self.scheduler.now())))
        else:
            await ctx.send(ShepherdCog.Messages['not_status'])

    @commands.command(help='Stores the number of pushups you did', description='Current exercise session \
has to have been announced in order for your score to apply (otherwise it\'s applied to the previous session).')
    async def did(self, ctx, count : int):
        # set last value to count
        chn = ctx.message.channel
        self.database.edit_last_stats(ctx.message.author.id, chn.id, count)
        # add funny reaction
        requested = ShepherdCog.Messages['did_reaction']
        emoji = discord.utils.find(lambda x : requested in str(x), self.bot.emojis)
        await ctx.message.add_reaction(ShepherdCog.Messages['did_reaction'])

    @commands.command(help='Shows stats for a user')
    async def stats(self, ctx, user: Optional[discord.Member] = None):
        if user is None:
            user = ctx.author
        chn = ctx.message.channel
        await ctx.send(self.str_members_stats(chn, [user]))

    @commands.command(help='Shows stats for all users in the current channel')
    async def allstats(self, ctx):
        chn = ctx.message.channel
        members = list(filter(lambda x: not x.bot, chn.members))
        await ctx.send(self.str_members_stats(chn, members))

    def str_members_stats(self,
            chn: discord.TextChannel,
            members: List[discord.Member]):
        values = ''
        max_len = len(max(members, key=lambda x : len(x.name)).name)
        for mem in members:
            data = self.database.get_user_stats(mem.id, chn.id)
            values += ShepherdCog.str_data(max_len, mem.name, data)
        header = ShepherdCog.str_header(values)
        return f'```\n{header}{values}\n```'

    @staticmethod
    def str_header(values):
        maxes = []
        elements = [l.split('│') for l in values.split('\n')]
        for i in range(3):
            maxes.append(max([ len(el[min(i, len(el)-1)]) for el in elements ]))
        res = 'name'.ljust(maxes[0]-1) \
            + ' │ avg'.ljust(maxes[1]+1) \
            + ' │ values'.ljust(maxes[2]-1) \
            + '\n'
        res += '{}┿{}┿{}\n'.format('━' * maxes[0], '━' * maxes[1], '━' * maxes[2])
        return res

    @staticmethod
    def str_data(maxlen, name, data):
        avg = 0
        m = ShepherdCog.StatsMax
        size = min(len(data), m)
        last = data[len(data)-size:]

        for i in range(size):
            avg += last[i]
        avg: float = avg / float(max(size, 1))
        str_avg = f'{avg:.2g}'
        return f'{name.ljust(maxlen)}  │ {str_avg.ljust(6)} │ {ShepherdCog.str_list(last)}\n'

    @staticmethod
    def str_list(lst):
        if len(lst) == 0:
            return "none"
        res = ''
        delim = ''
        for el in lst:
            res += f'{delim}{el}'
            delim = ' '
        return res

    def correct_time(self, time):
        # okay, this is terrible o_O
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

