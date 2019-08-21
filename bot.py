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
import numpy as np #getting min/max stuff
import re #regex stuff
import base64  #encoding stuff

cwd = Path(__file__).parents[0]
print(cwd)

def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("!")(bot, message)
    data = read_json('config')
    did = '{}'.format(message.guild.id)
    if did not in data:
        return commands.when_mentioned_or("!")(bot, message)
    prefix = data[did]['prefix']
    return commands.when_mentioned_or(prefix)(bot, message)

config_file = json.load(open(str(cwd)+'/bot_config/config.json'))
secret_file = json.load(open(str(cwd)+'/bot_config/secrets.json'))
did = "12345"
prefix = config_file[did]['prefix']
bot = commands.Bot(command_prefix=get_prefix, owner_id=271612318947868673, case_insensitive=True)
bot.remove_command('help')
bot.config_prefix = config_file[did]['prefix']
bot.config_token = secret_file['token']
extensions = []

botVersion = "0.3"

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
    ignored = (commands.CommandNotFound)
    if isinstance(error, ignored):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a `%.2fs` cooldown' % error.retry_after)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("This commands failed a check :/")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I am missing permissions to do this...")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.')
    channel = bot.get_channel(586147375781773312)
    await channel.send(f"An error occured:\n{error}")
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
async def prefix(ctx, *, pre):
    '''Set a custom prefix for the guild.'''
    #try find prefix for this server in existing data using result = data[etc etc]
    uid = '{0.id}'.format(ctx.message.author)
    did = '{}'.format(ctx.message.guild.id)
    data = read_json('config')
    if not did in data:
        #create new area for that discord then store guild prefix
        data[did] = {}
        data[did]['prefix'] = str(pre)
        write_json(data, 'config')
        return await ctx.send(f'The guild prefix has been set to `{pre}` Use `{pre}prefix <prefix>` to change it again.')
    data[did]['prefix'] = str(pre)
    #update json file for that discord
    write_json(data, 'config')
    await ctx.send(f'The guild prefix has been set to `{pre}` Use `{pre}prefix <prefix>` to change it again.')

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
    await asyncio.sleep(10)
    await ctx.message.delete()


@bot.command()
async def embed(ctx, *, content:str):
    embed = discord.Embed(description = content, color = discord.Color.orange())
    embed.set_footer(text = 'ID: ' + str(ctx.author.id))
    embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
    await ctx.send(embed = embed);
    await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def rollbatch(ctx, *, times):
    member = ctx.author
    for i in range(2):
        stuff = times
        easy = []
        bool = False
        end = 0
        args = None
        end = False
        print(stuff)
        for char in times:
            easy.append(str(char.lower()))
        length = len(easy)
        if i != 0:
            for i in range(length):
                if str(easy[i]) == ' ':
                    end = i
            times = stuff[new:]
            print(times)

        for x in range(length):
            if str(easy[x]) == '-' or str(easy[x]) == '+':
                for i in range(length):
                    if str(easy[i]) == ' ':
                        end = i
                        #print(easy[:end])
                add = times[int(x+1):int(end)]
                print(add)
                add = str(add)
                add = easy[x] + add
                print(add)
                print("---")
                add = int(add)
                bool = True
                break
        for i in range(length):
            if str(easy[i].lower()) == 'd':
                if bool == True:
                    sides = times[int(i+1):int(x)]
                else:
                    sides = times[int(i+1):int(end)]
                times = times[:int(i)]
                if not args:
                    args = "normal"
                times = int(times)
                sides = int(sides)
                break
        new = int(end) + 1
        print(stuff)
        if times == 0 or  sides == 0:
            await ctx.send("Yo bro you need to specify the parts I use\n `roll (how many times) (how many sided dice) (modifier)`")
        else:
            try:
                if 'disadv' in str(args.lower()) or 'disadvantage' in str(args.lower()):
                    embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\nRoll Type: Disadvantage', colour=member.colour)
                    result = disadvantageRoll(times, sides, add)
                    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
                elif 'adv' in str(args.lower()) or 'advantage' in str(args.lower()):
                    embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\nRoll Type: Advantage', colour=member.colour)
                    result = advantageRoll(times, sides, add)
                    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
                else:
                    embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\nRoll Type: Normal', colour=member.colour)
                    result = roll(times, sides, add)
                    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
            except:
                embed = discord.Embed(title='Roll:', description='Roll Type: **ERROR**', colour=member.colour)
                embed.add_field(name='**ERROR**', value='\uFEFF')
            embed.set_author(icon_url=member.avatar_url, name=str(member))
            bool = False
            print("One downs \n -----")
        await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
async def logout(ctx):
    """Log the bot out of discord"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
        await ctx.send("Logging out...")
        print(f"{ctx.message.author} has logged the bot out")
        await bot.logout()

#custom commands - The Wheel
@bot.command()#for times loop, random(1, sides). multiplier
async def roll(ctx, times=None, sides=None, *, args=None):
    await ctx.message.delete()
    member = ctx.author
    easy = []
    bool = False
    if "d" in times.lower():
        for char in times:
            easy.append(str(char.lower()))
        length = len(easy)
        for x in range(length):
            if str(easy[x]) == '-' or str(easy[x]) == '+':
                add = times[int(x+1):]
                add = str(add)
                add = easy[x] + add
                add = int(add)
                bool = True
                break
        if bool == False:
            try:
                num = re.sub('[^\d.,]' , '', str(sides))
                add = int(num)
                if "-" in sides:
                    add = "-"+ str(add)
                    add = int(add)
            except:
                add = 0
        for i in range(length):
            if str(easy[i].lower()) == 'd':
                if bool == True:
                    sides = times[int(i+1):int(x)]
                else:
                    sides = times[int(i+1):]
                times = times[:int(i)]
                if not args:
                    args = "normal"
                times = int(times)
                sides = int(sides)
                break
    else:
        if not times:
            times = 0
        if not sides:
            sides = 0
        times = int(times)
        sides = int(sides)
        try:
            num = re.sub('[^\d.,]' , '', str(args))
            add = int(num)
            if "-" in args:
                add = "-"+ str(add)
                add = int(add)
        except:
            add = 0
        if not args:
            args = "normal"
    if times == 0 or  sides == 0:
        await ctx.send("Yo bro you need to specify the parts I use\n `roll (how many times) (how many sided dice) (modifier)`")
    else:
        try:
            if 'disadv' in str(args.lower()) or 'disadvantage' in str(args.lower()):
                embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\nRoll Type: Disadvantage', colour=member.colour)
                result = disadvantageRoll(times, sides, add)
                embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
            elif 'adv' in str(args.lower()) or 'advantage' in str(args.lower()):
                embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\nRoll Type: Advantage', colour=member.colour)
                result = advantageRoll(times, sides, add)
                embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
            else:
                embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\nRoll Type: Normal', colour=member.colour)
                result = roll(times, sides, add)
                embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
        except:
            embed = discord.Embed(title='Roll:', description='Roll Type: **ERROR**', colour=member.colour)
            embed.add_field(name='**ERROR**', value='\uFEFF')
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        await ctx.send(embed=embed)
        #await ctx.message.delete()

@bot.command(name='setskill', aliases=["skillset"])
async def _setskill(ctx, skill=None, change=None, type="normal"):
    if 'disadv' in str(type.lower()) or 'disadvantage' in str(type.lower()):
        type = "disadvantage"
    elif 'adv' in str(type.lower()) or 'advantage' in str(type.lower()):
        type = "advantage"
    else:
        type = "normal"
    if skill != None and change != None:
        data = read_json('users')
        uid = '{0.id}'.format(ctx.message.author)
        did = '{}'.format(ctx.message.guild.id)
        name = '{}'.format(ctx.message.author)
        if did in data:#if the discord is already in data
            if uid in data[did]:
                if skill in data[did][uid]:
                    data[did][uid][f'{skill}']['value'] = change
                    data[did][uid][f'{skill}']['type'] = type
                else:
                    data[did][uid][skill] = {}
                    data[did][uid][f'{skill}']['value'] = change
                    data[did][uid][f'{skill}']['type'] = type
            else:
                data[did][uid] = {}
                if skill in data[did][uid]:
                    data[did][uid][f'{skill}']['value'] = change
                    data[did][uid][f'{skill}']['type'] = type
                else:
                    data[did][uid][skill] = {}
                    data[did][uid][f'{skill}']['value'] = change
                    data[did][uid][f'{skill}']['type'] = type
        else:#if the discord isnt in the data
                data[did] = {}
                if uid in data[did]:
                    if skill in data[did][uid]:
                        data[did][uid][f'{skill}']['value'] = change
                        data[did][uid][f'{skill}']['type'] = type
                    else:
                        data[did][uid][skill] = {}
                        data[did][uid][f'{skill}']['value'] = change
                        data[did][uid][f'{skill}']['type'] = type
                else:
                    data[did][uid] = {}
                    if skill in data[did][uid]:
                        data[did][uid][f'{skill}']['value'] = change
                        data[did][uid][f'{skill}']['type'] = type
                    else:
                        data[did][uid][skill] = {}
                        data[did][uid][f'{skill}']['value'] = change
                        data[did][uid][f'{skill}']['type'] = type
        write_json(data, 'users')
        member = ctx.author
        embed = discord.Embed(title='Skill Data Changed:', description=f'Skill: `{skill}`\nSkill Value: `{change}`\nSkill Type: `{type}`', colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        await ctx.send(embed=embed)
        await ctx.message.delete()
    else:
        msg1 = await ctx.send("I need you to do the command like so....\n `skillset (the skill) (what I should set it to)` `(skill type - optional)`")
        msg2 = await ctx.send(f"If you would like to see your current saved skills please use {bot.config_prefix}skills")
        await ctx.message.delete()
        await asyncio.sleep(10)
        await msg1.delete()
        await msg2.delete()

@bot.command()
@commands.guild_only()
async def skills(ctx):
    uid = '{0.id}'.format(ctx.message.author)
    did = '{}'.format(ctx.message.guild.id)
    member = ctx.author
    data = read_json('users')
    if did in data:#if the discord is already in data
        if uid in data[did]:
            await member.send(f"Here are your skills for the discord: (`{ctx.message.guild}`).")
            for skill in data[did][uid]:
                await member.send(f"Skill: `{skill}`. Skill value: `{data[did][uid][skill]['value']}`. Skill type: `{data[did][uid][skill]['type']}`.")
            msg = await ctx.send(f"Hey <@{uid}>, please check your dms from me")
        else:
            msg = await member.send(f"Hey <@{uid}>. Im sorry you (`{uid}`) don't exist within my data so I cannot show your skills :shrug:")
    else:
        msg = await member.send(f"Hey <@{uid}>. Im sorry either your discord (`{did}`), or you (`{uid}`), don't exist within my data so I cannot show your skills :shrug:")
    await ctx.message.delete()
    await asyncio.sleep(10)
    await msg.delete()

@bot.command(name='rollskill', aliases=['skillroll'])
async def _rollskill(ctx, skill=None, type=None):
    data = read_json('users')
    uid = '{0.id}'.format(ctx.message.author)
    did = '{}'.format(ctx.message.guild.id)
    member = ctx.author
    if did in data:#if the discord is already in data
        if uid in data[did]:
            if skill in data[did][uid]:
                skillName = skill
                skillValue = data[did][uid][skill]['value']
                if not type:
                    skillType = data[did][uid][skill]['type']
                else:
                    skillType = type
                times = 1
                sides = 20
                add = int(skillValue)
                if 'disadv' in str(skillType.lower()) or 'disadvantage' in str(skillType.lower()):
                    embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\n Skill: {skill}\nRoll Type: Disadvantage', colour=member.colour)
                    result = disadvantageRoll(times, sides, add)
                    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
                elif 'adv' in str(skillType.lower()) or 'advantage' in str(skillType.lower()):
                    embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\n Skill: {skill}\nRoll Type: Advantage', colour=member.colour)
                    result = advantageRoll(times, sides, add)
                    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
                else:
                    embed = discord.Embed(title='Roll:', description=f'Rolled: {times}d{sides}\n Skill: {skill}\nRoll Type: Normal', colour=member.colour)
                    result = roll(times, sides, add)
                    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
                embed.set_author(icon_url=member.avatar_url, name=str(member))
                await ctx.send(embed=embed)
            else:
                msg = await ctx.send(f"Im sorry, you do not have a skill called `{skill}`.\nIf you wish to see what skills you do have please run {bot.config_prefix}skills")
                await asyncio.sleep(10)
                await msg.delete()
        else:
            msg = await ctx.send(f"Hey <@{uid}>. Im sorry you (`{uid}`) don't exist within my data so I cannot roll your skills :shrug:")
            await asyncio.sleep(10)
            await msg.delete()
    else:
        msg = await ctx.send(f"Hey <@{uid}>. Im sorry either your discord (`{did}`), or you (`{uid}`), don't exist within my data so I cannot show your skills :shrug:")
        await asyncio.sleep(10)
        await msg.delete()
    await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def test(ctx):
    member = ctx.author
    result = disadvantageRoll(5,15,15)
    embed = discord.Embed(title='Roll:', description='*Disadvantage*', colour=member.colour)
    embed.add_field(name=f'The total is: **{result[0]}**', value=f'{result[1]}')
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
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
    try:
        color = ctx.author.colour
    except:
        color = 0xffb000
    embed = discord.Embed(title='{} Stats'.format(bot.user.name), description='\uFEFF', colour=color)
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
    await ctx.message.delete()

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
    msg = await ctx.send(f"Hey {member.mention}, please check your dms from me")
    await asyncio.sleep(10)
    await ctx.message.delete()
    await msg.delete()

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
