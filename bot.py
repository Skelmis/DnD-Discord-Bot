import discord #required
from discord.ext import commands #required
from aiohttp import ClientSession
import aiohttp
import asyncio
import os #replaced by pathlib?
import json #for jsons
import math #math functions
import datetime #for date/time stuff
import sys #stats
import platform #stats
import random #random numbers
import pathlib #path stuff
from pathlib import Path #getting paths
import numpy as np
import re #regex stuff
import base64  #encoding stuff

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
    bot.config_token = bot.config_token.swapcase()
    bot.config_token = bot.config_token.encode("cp037", "replace")
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
    #if message.channel.id == 503773157962809344:
    #    if "accept" in message.clean_content.lower():
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
    print(ctx, error)
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a `%.2fs` cooldown' % error.retry_after)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("This commands failed a check :/")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("FUck")
    raise error  # re-raise the error so all the errors will still show up in console

@bot.event
async def on_command_completion(ctx):
    data = read_json('secrets')
    count = data['cc']
    count += 1
    data['cc'] = count
    write_json(data, 'secrets')

#@bot.command(name='eval')
#@commands.is_owner()
#async def _eval(ctx, *, code):
#    """A bad example of an eval command"""
#    await ctx.send(eval(code))

@bot.command()
async def react(ctx):
    botmsg = await ctx.send('Are you sure?')
    await botmsg.add_reaction('👍')
    await botmsg.add_reaction('👎')
    channel = ctx.channel
    mlg = await channel.history().get(author=bot.user)
    print(mlg)
    await asyncio.sleep(5)
    cache_msg = discord.utils.get(mlg, id=botmsg.id)
    #cache_msg.reactions
    for item in cache_msg.reactions:
            print(item)

    #users = await reaction.users().flatten()
    # users is now a list...
    #winner = random.choice(users)
    #await ctx.send(users)
    #await channel.send('{} has won the raffle.'.format(winner))

@bot.command()
@commands.has_any_role('Config')
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
    embed = discord.Embed(description = content, color = discord.Color.orange())
    embed.set_footer(text = 'ID: ' + str(ctx.author.id))
    embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
    await ctx.send(embed = embed);





#custom commands - The Wheel
@bot.command()#for times loop, random(1, sides). multiplier
async def roll(ctx, times=0, sides=0, *, args=None):
    member = ctx.author
    times = int(times)
    sides = int(sides)
    try:
        num = re.sub('[^\d.,]' , '', str(args))
        add = int(num)
    except:
        add = 0
    if times == 0 or  sides == 0:
        await ctx.send("Yo bro you need to specify the parts I use\n `roll (how many times) (how many sided dice) (modifier)`")
    else:
        try:
            if 'disadv' in str(args.lower()) or 'disadvantage' in str(args.lower()):
                embed = discord.Embed(title='Roll:', description='Roll Type: Disadvantage', colour=member.colour)
                result = disadvantageRoll(times, sides, add)
                embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
            elif 'adv' in str(args.lower()) or 'advantage' in str(args.lower()):
                embed = discord.Embed(title='Roll:', description='Roll Type: Advantage', colour=member.colour)
                result = advantageRoll(times, sides, add)
                embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
            else:
                embed = discord.Embed(title='Roll:', description='Roll Type: Normal', colour=member.colour)
                result = roll(times, sides, add)
                embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
        except:
            embed = discord.Embed(title='Roll:', description='Roll Type: **ERROR**', colour=member.colour)
            embed.add_field(name='**ERROR**', value='\uFEFF')
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        await ctx.send(embed=embed)

@bot.command()
async def setskill(ctx, skill=None, change=None):
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


@bot.command()
async def test(ctx):
    member = ctx.author
    result = disadvantageRoll(5,15,15)
    embed = discord.Embed(title='Roll:', description='*Disadvantage*', colour=member.colour)
    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    await ctx.send(embed=embed)

@bot.command()
async def accept(ctx, member: discord.Member, *args):
    if "accept" in args:
        role = discord.utils.get(member.guild.roles, name="Members")
        await member.add_roles(role)
        await ctx.message.delete()
        removerole = discord.utils.get(member.guild.roles, name="Unverified")
        await member.remove_roles(removerole)
    else:
        ctx.message.delete()

#functions
def roll(times, sides, add):
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
    calcNum = f"{calcNum} + ({add})"
    total = total + add
    return str(total), calcNum

def disadvantageRoll(times, sides, add):
    a = []
    b = []
    for i in range(2):
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
        calcNum = f"{calcNum} + ({add})"
        total = total + add
        a.append(total)
        b.append(calcNum)
    lowRoll = min(a)
    ind = np.argmin(a)
    lowRollMath = b[ind]
    return str(lowRoll), lowRollMath

def advantageRoll(times, sides, add):
    a = []
    b = []
    for i in range(2):
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
        calcNum = f"{calcNum} + ({add})"
        total = total + add
        a.append(total)
        b.append(calcNum)
    highRoll = max(a)
    ind = np.argmax(a)
    highRollMath = b[ind]
    return str(highRoll), highRollMath

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
    member = ctx.author
    await member.trigger_typing()
    help_file = open(str(cwd)+'/bot_config/help.txt', 'r')
    em = discord.Embed(colour=0xffb000)
    em.add_field(name ='-', value=help_file.read(), inline=False)
    em.set_footer(text="() - Required | <> - Optional")
    help_file.close()
    await asyncio.sleep(1)
    await member.send(embed=em)

#cogs commands are different.
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
    bot.config_token = bot.config_token.swapcase()
    bot.run(bot.config_token)
