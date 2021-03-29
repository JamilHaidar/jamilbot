import datetime
import os
import config as c
from inspect import signature
from cogs.utils.checks import user_is_developer
import discord
from discord.ext import commands


class HelpCog(commands.Cog, name="Help"):
    """ HelpCog """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['man'])
    async def help(self, ctx, *, command: str = ''):
        """ General bot help.
            https://docs.python.org/3/library/inspect.html
        """
        gearIcon = "https://i.ibb.co/TwwnHXQ/gear.png"
        if not command:
            helpEmbed = discord.Embed(title='', timestamp=datetime.datetime.utcnow(), description=f'```apache\n{", ".join(c.prefixes)}```', color=discord.Color.from_rgb(48, 105, 152))
            helpEmbed.set_footer(text='All Commands', icon_url=gearIcon)
            for cog in self.bot.cogs:
                body = ''
                for cmd in self.bot.commands:
                    try:
                        if not await cmd.can_run(ctx):continue
                    except:
                        continue
                    if str(cmd.cog.qualified_name) == str(cog) and not cmd.hidden:
                        nameAliases = str(cmd) if not ' | '.join(cmd.aliases) else '['+str(' | '.join(str(cmd).split(" ")+cmd.aliases)+']')
                        body += '  • '+nameAliases+'\n'
                if body =='':continue
                helpEmbed.add_field(name=str(cog), value=body, inline=False)
            await ctx.send(embed=helpEmbed)
            return

        cog = self.bot.get_cog(command)
        if cog is None:
            cog = self.bot.get_cog(command.title())
        if command and cog is not None:
            cogEmbed = discord.Embed(title='', timestamp=datetime.datetime.utcnow(), description=f'```\n{cog.description}```', color=discord.Color.from_rgb(0, 14, 40))
            cogEmbed.set_footer(text=cog.qualified_name, icon_url=gearIcon)

            body = ''
            for cmd in self.bot.commands:
                if str(cmd.cog.qualified_name) == str(cog.qualified_name) and not cmd.hidden:
                    nameAliases = str(cmd) if not ' | '.join(cmd.aliases) else '['+str(' | '.join(str(cmd).split(" ")+cmd.aliases)+']')
                    body += '  • '+nameAliases+'\n'

            cogEmbed.add_field(name='Commands', value=body, inline=False)

            await ctx.send(embed=cogEmbed)
            return

        for cmd in self.bot.commands:
            if str(cmd) == str(self.bot.get_command(command)):
                nameAliases = str(cmd) if not ' | '.join(cmd.aliases) else '['+str(' | '.join(str(cmd).split(" ")+cmd.aliases)+']')
                usage = f'{ctx.prefix}{cmd}'
                for key, value in cmd.clean_params.items():
                    usage += f' {value}'
                commandEmbed = discord.Embed(title='',
                        timestamp=datetime.datetime.utcnow(),
                        description=f'```jb\n{usage}```\n{cmd.help}', color=discord.Color.from_rgb(194, 124, 13))
                commandEmbed.set_author(name=nameAliases, icon_url=str(ctx.message.guild.get_member(ctx.message.author.id).avatar_url))
                commandEmbed.set_footer(text=cmd.cog.qualified_name, icon_url=gearIcon)

                await ctx.send(embed=commandEmbed)
                return

def setup(bot):
    bot.remove_command('help')
    bot.add_cog(HelpCog(bot))
