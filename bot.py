import discord
from discord.ext import commands
from aiohttp import ClientSession
import aiohttp
import asyncio
import async_timeout
import os
import json
import math
import datetime
import sys
import platform
import random
import pathlib
from pathlib import Path
cwd = Path(__file__).parents[0]
print(cwd)

config_file = json.load(open(str(cwd)+'/bot_config/config.json'))
secret_file = json.load(open(str(cwd)+'/bot_config/secrets.json'))
did = "12345"
prefix = config_file[did]['prefix']
bot = commands.Bot(command_prefix=prefix, owner_id=271612318947868673)
bot.remove_command('help')
bot.config_prefix = config_file[did]['prefix']
bot.config_token = secret_file['token']
extensions = []

botVersion = "0.1"

@bot.event
async def on_ready():
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="my favorite friends."))
    member = bot.get_user(271612318947868673)
    await member.send(f"{bot.user.name} is now online...")

@bot.event
async def on_message(message):
    #if bot.config_prefix in message:
    #    await message.add_reaction('👀') # :eyes:
    await bot.process_commands(message)

#No longer needed due to carl bot
#@bot.event
#async def on_message_delete(message):
#    author = message.author
#    deleteChannel = message.channel
#    content = message.content
#    discord = message.guild.name
#    channel = bot.get_channel(563875550205181952)
#    await channel.send('#{} -> user {} deleted: `{}`'.format(deleteChannel, author, content))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a `%.2fs` cooldown' % error.retry_after)
    raise error  # re-raise the error so all the errors will still show up in console

@bot.event
async def on_command_completion(ctx):
    data = read_json('secrets')
    count = data['cc']
    count += 1
    data['cc'] = count
    write_json(data, 'secrets')


@bot.command()
async def echo(ctx,*,msg='e'):
    if msg == 'e':
        await ctx.send("Please enter text to echo after the command")
    else:
        await ctx.channel.purge(limit=1)
        await ctx.send(msg)

#@bot.event
#async def on_member_join(user):
#    member = user.id
#    channel = bot.get_channel(bot.config_welcomeChannel)
#    await channel.send("Welcome <@{}>. Use % apply to join the faction!".format(member))

spamcount = 0
@bot.command()
@commands.is_owner()
async def spam(ctx, *, message):
    global spamcount
    while spamcount < 5:
        await ctx.send("{}".format(message))
        spamcount += 1
    else:
        await ctx.send("Reset")
        spamcount = 0

@bot.command()
@commands.has_any_role('Config')
async def purge(ctx, amount:int):
    amount += 1
    await ctx.channel.purge(limit=amount)

@bot.command()
async def modules(ctx):
    await ctx.send("Current Modules:")
    await asyncio.sleep(1)
    for extension in extensions:
        await ctx.send(extension)
        await asyncio.sleep(0.5)

@bot.command(name='perms', aliases=['perms_for', 'permissions', 'userperms'])
@commands.guild_only()
async def check_permissions(ctx, member: discord.Member=None):
    """A simple command which checks a members Guild Permissions.
    If member is not provided, the author will be checked."""
    if not member:
        member = ctx.author
    # Here we check if the value of each permission is True.
    perms = '\n'.join(perm for perm, value in member.guild_permissions if value)
    # And to make it look nice, we wrap it in an Embed.
    embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
    embed.add_field(name='\uFEFF', value=perms)
    await ctx.send(content=None, embed=embed)


@bot.command()
async def embed(ctx, *, content:str):

    # Usage: (prefix)embed <your message>

    embed = discord.Embed(
        description = content,
        color = discord.Color.orange()
    );

    embed.set_footer(text = 'ID: ' + str(ctx.author.id));
    embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url));

    await ctx.send(embed = embed);



#custom commands - The Wheel
@bot.command()#for times loop, random(1, sides). multiplier
async def roll(ctx, times=0, sides=0, add=0):
    member = ctx.author
    times = int(times)
    sides = int(sides)
    add = int(add)
    embed = discord.Embed(title='Roll:', description='\uFEFF', colour=member.colour)
    if times == 0 or  sides == 0:
        await ctx.send("Yo bro you need to specify the parts I use\n `roll (how many times) (how many sided dice) (modifier)`")
    else:
        total = 0
        calcNum = ""
        for x in range(times):
            sideNum = random.randint(1, sides)
            total = total + sideNum
            if calcNum == "":
                sideNum = str(sideNum)
                calcNum = f"{sideNum}"
            else:
                sideNum = str(sideNum)
                calcNum = f"{calcNum} + {sideNum}"
        total = total + add
        if add == 0:
            embed.add_field(name=f'The total is: **{total}**', value=f'{calcNum}')
        else:
            print("Hi")
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        await ctx.send(embed=embed)

@bot.command()
async def skillset(ctx, skill=None, change=None):
    if skill != None and change != None:
        data = read_json('users')
        uid = '{0.id}'.format(ctx.message.author)
        did = '{}'.format(ctx.message.guild.id)
        name = '{}'.format(ctx.message.author)
        if did in data:#if the discord is already in data
            if uid in data[did]:
                data[did][uid][f'{skill}'] = change
            else:
                data[did][uid] = {}
                data[did][uid][f'{skill}'] = change
        else:#if the discord isnt in the data
                data[did] = {}
                if uid in data[did]:
                    data[did][uid][f'{skill}'] = change
                else:
                    data[did][uid] = {}
                    data[did][uid][f'{skill}'] = change
        write_json(data, 'users')
    else:
        await ctx.send("I need you to do the command like so....\n `skillset (the skill) (what I should set it to)`")





#functions
def addspace(n):
    w = ''
    for x in range(0, n):
        w = w + ' '
    return w

def read_json(filename):
    jsonFile = open(str(cwd)+'/bot_config/'+filename+'.json', 'r')
    data = json.load(jsonFile)
    jsonFile.close()
    return data

def write_json(data, filename):
    jsonFile = open(str(cwd)+'/bot_config/'+filename+'.json', 'w+')
    jsonFile.write(json.dumps(data))
    jsonFile.close()

@bot.command()
async def stats(ctx):
    data = read_json('secrets')
    pythonVersion = platform.python_version()
    rewriteVersion = discord.__version__
    #loop for members
    botServers = bot.guilds
    serverCount = 0
    for guild in botServers:
        serverCount += 1
    userCount = 0
    for g in botServers:
        userCount += len(g.members)
    embed = discord.Embed(title='{} Stats'.format(bot.user.name), description='\uFEFF', colour=ctx.author.colour)
    embed.add_field(name='Bot Version:', value=botVersion)
    embed.add_field(name='Python Version:', value=pythonVersion)
    embed.add_field(name='Discord.Py Version', value=rewriteVersion)
    embed.add_field(name='Total Guilds:', value=serverCount)
    embed.add_field(name='Total Users:', value=userCount)
    embed.add_field(name='Total commands run:', value=data['cc'])
    embed.add_field(name='Bot Developer:', value="<@271612318947868673>")
    embed.set_footer(text="Carpe Noctem | {} | Nerd Cave Development".format(bot.user.name))
    embed.set_author(name = str(bot.user.name), icon_url = str(bot.user.avatar_url))
    await ctx.send(embed = embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Commands', description='\uFEFF', colour=ctx.author.colour)
    embed.add_field(name='stats', value='\uFEFF')
    embed.add_field(name='embed', value='\uFEFF')
    embed.add_field(name='purge', value='\uFEFF')
    embed.add_field(name='spam', value='\uFEFF')
    embed.add_field(name='perms', value='\uFEFF')
    embed.add_field(name='modules', value='\uFEFF')
    embed.add_field(name='echo', value='\uFEFF')
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    if extension in extensions:
        try:
            bot.load_extension(extension)
            await ctx.send('Loaded module {}'.format(extension))
        except Exception as error:
            await ctx.send('{} module cannont be loaded. [{}]'.format(extension, error))

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    if extension in extensions:
        try:
            bot.unload_extension(extension)
            await ctx.send('Unloaded module {}'.format(extension))
        except Exception as error:
            await ctx.send('{} module cannont be unloaded. [{}]'.format(extension, error))

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print("Loaded extension {}".format(extension))
        except Exception as error:
            print('{} cannont be loaded. [{}]'.format(extension, error))
    bot.run(bot.config_token)
