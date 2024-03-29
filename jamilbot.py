from inspect import istraceback
import discord
from discord.ext import commands
import os
import sys
import logging
import re
import random
import datetime
import asyncio

import config as c
from cogs.utils import rules

from app.main import app
from threading import Thread
def app_run():
    try:
        PORT = os.environ.get('PORT')
        app.run(host="0.0.0.0", port=PORT)
    except:
        app.run(host="0.0.0.0",port='8080')
app_thread = Thread(target=app_run)
app_thread.start()

# COGS = ['cogs.owner',
#         'cogs.commands',
#         'cogs.admin',
#         'cogs.dev',
#         'cogs.osu',
#         'cogs.memes',
#         'cogs.runners',
#         'cogs.help'
#         ]

COGS = ['cogs.owner',
        'cogs.admin',
        'cogs.dev',
        'cogs.help',
        'cogs.memes']

# DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(levelname)-8s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S'
                    )
log = logging.getLogger(__name__)


def get_prefix(_bot, message):
    """
    Return the prefix used in the specific channel.
    """
    return commands.when_mentioned_or(*c.prefixes)(_bot, message)



intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=get_prefix,description=c.description,intents=intents,case_censitive=False)

@bot.event
async def on_ready():
    '''
    Bot is ready!
    '''
    print('Bot ready!')
    joined_guilds = []
    for guild in bot.guilds:
        joined_guilds.append(f' - {str(guild.id).ljust(20)} {guild.name}')

    ready_message = [
        'Logged in as:',
        f'{bot.user.name}: {bot.user.id}',
        f'Discord Version: {discord.__version__}',
        f'\nBot currently running on {len(bot.guilds)} server(s):',
        '\n'.join(joined_guilds)
    ]

    log.info('\n'.join(ready_message))

    await bot.change_presence(status=discord.Status.online, activity=discord.Game('with Java!'))

@bot.event
async def on_message(message):
    """
    When a message is sent in a channel the bot is a member of.
    """
    if message.author == bot.user or message.author.bot:
        return
    try:
        if str(rules.getrule('prefixless', message.guild.id)).lower() == 'true':
            if re.compile(r'(\s+|^)(' + '|'.join(c.swears) + ')(\s+|$)').search(message.content.lower()):
                await message.add_reaction(random.choice(c.rages))
                log.info(message)
            if message.content.startswith('man '):
                message.content = message.content.replace('man ', c.prefixes[0]+'help ')
            if message.content.upper() == 'F':
                await message.channel.send('F')
        if str(rules.getrule('self-harm', message.guild.id)).lower() == 'true':
            if re.compile(r'(\s+|^)(' + '|'.join(c.harms) + ')(\s+|$)').search(message.content.lower()):
                await message.add_reaction(random.choice(c.sads))
                embed = discord.Embed(title='',
                            url='https://jamil-bot.herokuapp.com/embrace',
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.from_rgb(200, 0, 0))
                embed.description = "If you're not feeling well. Talk about it. Contact Embrace at [1564](https://jamil-bot.herokuapp.com/embrace), or [here](https://embracelebanon.org/embrace-lifeline/)."
                await message.channel.send(embed=embed)
                log.info(message)
        if str(rules.getrule('dad', message.guild.id)).lower() == 'true':
            dads = ["i\'m ","im ","ana ", "i am ", "jeg er ", "ich bin ", "ik ben ", "jag är ", "æ e "]
            for dad in dads:
                if message.content.lower().startswith(dad):
                    if dad in message.content.lower():
                        await message.channel.send(random.choice(c.greetings)+', '+message.content[int(message.content.lower().find(dad))+len(dad):].strip()+'! I\'m ClassBot.')
                        log.info(message)
    except Exception as e:
        print(e)
    log.info("[%s]%s> %s" % (message.guild.name, message.author.name, message.content))
    await bot.process_commands(message)

# @bot.event
# async def on_voice_state_update(member,before,after):
#     vc = discord.utils.get(bot.voice_clients,guild=member.guild)
#     if not(vc is None):
#         if len(vc.channel.members)==1:
#             await vc.disconnect()


@bot.event
async def on_error(error):
    """
    Whan an error occurs.
    """
    log.error('An unexpected error occurred: %s', error)

@bot.event
async def on_command_error(self, exception):
    """
    When a command fails.
    """
    log.info(exception)
    if isinstance(exception, commands.errors.MissingPermissions):
        exception = f'Sorry {self.message.author.name}, you don\'t have permissions to do that!'
    elif isinstance(exception, commands.errors.CheckFailure):
        exception = f'Sorry {self.message.author.name}, you don\'t have the necessary roles for that!'
    elif isinstance(exception, TimeoutError):
        log.warn(f'TimeoutError: {exception}')
        return
    elif isinstance(exception,commands.errors.DisabledCommand):
        exception = f'Sorry {self.message.author.name}, that command is disabled!'
    error_embed = discord.Embed(title='',
                                timestamp=datetime.datetime.utcnow(),
                                description=f'```css\n{exception}```',
                                color=discord.Color.from_rgb(200, 0, 0))
    error_embed.set_author(name='Woops!',
                           icon_url=str(self.message.author.avatar_url))
    error_embed.set_footer(text=str(type(exception).__name__))
    error_message = await self.send(embed=error_embed)

    await error_message.add_reaction('❔')

    def check_reaction(reaction, user):
        return user != self.bot.user and str(reaction.emoji) == '❔'
    try:
        reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check_reaction)
    except asyncio.TimeoutError:
        await error_message.remove_reaction('❔', self.bot.user)
    else:
        await error_message.remove_reaction('❔', self.bot.user)
        error_embed.add_field(name='Details', value=f'{exception.__doc__}', inline=False)
        error_embed.add_field(name='Cause', value=f'{exception.__cause__ }', inline=False)
        await error_message.edit(embed=error_embed)

if __name__ == '__main__':
    for cog in COGS:
        bot.load_extension(cog)

    log.debug('Starting bot...')
    bot.run(c.data["botToken"], bot=True, reconnect=True)

# app_thread.join()
# bot.logout()



