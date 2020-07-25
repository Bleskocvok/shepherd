#!/usr/bin/env python3

import os
import discord
import asyncio
from discord.ext import commands

import perform


loop = asyncio.get_event_loop()


def job(chn : discord.TextChannel):
    # some coroutine hackery
    future  = asyncio.run_coroutine_threadsafe(chn.send('@everyone Exercise time!'), loop)
    future.result()


def correct_time(time):
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


def save(time : str, ID : int):
    with open('data/time.txt', 'w') as file:
        file.write(time + '\n')
        file.write(str(ID) + '\n')


def load():
    with open('data/time.txt', 'a') as file:
        pass
    with open('data/time.txt', 'r') as file:
        lines = file.readlines()
        if (len(lines) >= 2):
            return (lines[0].strip(), int(lines[1].strip()))
    return (None, None)


'''
MAIN
'''
token = ''
with open('secret_token.txt', 'r') as f:
    token = f.read().strip()

client = commands.Bot(command_prefix='!')

# initialize the object to perform the actions
per = perform.Perform()

if not os.path.isdir('./data'):
    os.mkdir('data')


'''
ASYNC CALLBACKS
'''
@client.event
async def on_ready():
    print('{} connected'.format(client.user.name))
    time, ID = load()
    channel = client.get_channel(ID)
    if (time != None and channel != None):
        per.scheduler(time)(job, channel)


@client.command(name='schedule', help='Schedules a time for exercise')
async def schedule(ctx, time):
    time = time.strip()
    if time[len(time) - 1] == '\n':
        time = time[:len(time) - 1]
    if not correct_time(time):
        await ctx.send('```Incorrect time format\nCorrect format is \'XX:XX\'```')
        return
    save(time, ctx.message.channel.id)
    per.scheduler(time)(job, ctx.message.channel)
    await ctx.send('```Scheduled exercise for {} in channel {}```'.format(time, ctx.message.channel.name))


@client.command(name='did', help='[To be done] Stores the number of pushups you did')
async def did(ctx, count : int):
    pass


@client.command(name='cancel', help='Cancels scheduled exercise')
async def cancel(ctx):
    per.cancel()
    save('', 0)
    await ctx.send('```Cancelled scheduled exercise for in channel {}```'.format(ctx.message.channel.name))


@client.command(name='stats', help='[To be done]')
async def stats(ctx, name):
    pass


'''
@client.event
async def on_command_error(ctx, error):
    print(error)
'''


'''
START
'''
client.run(token)


