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
        'cogs.admin']

# DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    #format='[%(asctime)s] [' + '%(levelname)s'.ljust(9) + '] %(name)s %(message)s',
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
        if str(rules.getrule('dad', message.guild.id)).lower() == 'true':
            dads = ["i\'m", "i am", "jeg er", "ich bin", "ik ben", "jag är", "æ e"]
            for dad in dads:
                if message.content.lower().startswith(dad):
                    if dad in message.content.lower():
                        await message.channel.send(random.choice(c.greetings)+', '+message.content[int(message.content.lower().find(dad))+len(dad):].strip()+'! I\'m JamilBot.')
                        log.info(message)
    except Exception as e:
        print(e)
    log.info("[%s]%s> %s" % (message.guild.name, message.author.name, message.content))
    await bot.process_commands(message)

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

@bot.command()
async def load(ctx,extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx,extension):
    bot.unload_extension(f'cogs.{extension}')

if __name__ == '__main__':
    for cog in COGS:
        bot.load_extension(cog)

    log.debug('Starting bot...')
    bot.run(c.data["botToken"], bot=True, reconnect=True)
    
# bot.logout()

# @bot.event
# async def on_ready():
#     print('Bot ready')

# @bot.event
# async def on_voice_state_update(member,before,after):
#     vc = discord.utils.get(bot.voice_clients,guild=member.guild)
#     if not(vc is None):
#         if len(vc.channel.members)==1:
#             await vc.disconnect()
            
# @bot.command()
# async def forcenudes(context):
#     await context.send(file=discord.File(f'{str(os.path.dirname(os.path.realpath(__file__)))}/img/anoose.jpg'))
#     await context.send(f'Come {context.message.author.mention}. *~~He?~~* She\'s waiting for you!')

# @bot.command()
# async def ping(context):
#     await context.send(f'Pong! {round(bot.latency * 1000)}ms')

# @bot.command()
# async def start_class(context):

#     # output = ''   
#     # for member in context.guild.members:
#     #     output+=f'name: {member.name}, bot: {member.bot}\n'
#     # await context.send(output)

#     if context.author.voice is None:
#         await context.send('Please join a voice channel first!')
#     else:
#         channel = context.author.voice.channel
#         await channel.connect()

#         for member in context.guild.members:    
#             # print(member.name,member.status)
#             # print(member.raw_status)
#             if member.bot:continue
#             # if member.offline:continue
#             if not(member.voice is None):
#                 if not(member.voice.channel is None):
#                     await member.move_to(channel=channel, reason='Class started.')
#             else:
#                 await member.send('Class is starting! ')
#                 invitation = await channel.create_invite(max_uses=1,max_age=7200,reason='Class starting.')
#                 dm = await member.create_dm()
#                 await dm.send(invitation)

# @bot.command()
# async def end_class(context):
#     vc = discord.utils.get(bot.voice_clients,guild=context.guild)
    
#     for member in context.guild.members:
#         if member.bot:continue
#         if not(member.voice is None):
#             if not(member.voice.channel is None):
#                 await member.move_to(channel=None,reason='Class ended.')
#         else:
#             dm = await member.create_dm()
#             await dm.send('Class ended.')
    
#     if not(vc is None):
#         invites = await vc.channel.invites()
#         for invite in invites:
#             await invite.delete(reason='Class ended. Removing all invites.')
#         await vc.disconnect()

# @bot.command()
# async def join(context):
#     if context.author.voice is None:
#         await context.send('Please join a voice channel first!')
#     else:
#         channel = context.author.voice.channel
#         await channel.connect()

# @bot.command()
# async def leave(context):
#     await context.voice_client.disconnect()

# @bot.command()
# async def clear(context,amount=5):
#     await context.purge(limit=amount)

# # @bot.command()
# # async def purge(context,timing,n_msgs=1):
# #     if timing=='before':
# #         pass
# #     elif timing=='after':
# #         pass
# #     elif timing == 'all':
# #         await context.channel.purge(oldest_first=True)
# #     else:
# #         context.send('Please select a viable timing (before|after|all).')

