import git
import inspect
import config as c

#from phue import Bridge
from discord.ext import commands
from importlib import reload


class OwnerCog(commands.Cog, name="Owner"):
    """ OwnerCog """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='configflush', aliases=['flush'], hidden=True)
    @commands.is_owner()
    async def _config_flush(self, ctx):
        """ Reload config.
        """
        reload(c)
        await ctx.send('```Successully reloaded config file.```')

    @commands.command(name='load', hidden=True, aliases=['l', 'lo'])
    @commands.is_owner()
    async def _load(self, ctx, *, cog: str):
        """ Command which Loads a Module.
            Remember to use dot path. e.g: cogs.owner
        """
        try:
            self.bot.load_extension(cog)
        except (AttributeError, ImportError) as error:
            await ctx.message.add_reaction('👎')
            await ctx.send(f'```py\nCould not load {cog}: {type(error).__name__} - {error}\n```')
        else:
            await ctx.message.add_reaction('👌')
            await ctx.send(f'```Successfully loaded {cog}!```')

    @commands.command(name='unload', hidden=True, aliases=['ul', 'unl'])
    @commands.is_owner()
    async def _unload(self, ctx, *, cog: str):
        """ Command which Unloads a Module.
            Remember to use dot path. e.g: cogs.owner
        """
        try:
            self.bot.unload_extension(cog)
        except (AttributeError, ImportError) as error:
            await ctx.message.add_reaction('👎')
            await ctx.send(f'```py\nCould not unload {cog}: {type(error).__name__} - {error}\n```')
        else:
            await ctx.message.add_reaction('👌')
            await ctx.send(f'```Successfully unloaded {cog}!```')



    @commands.command(name='reload', hidden=True, aliases=['r', 'rel'])
    @commands.is_owner()
    async def _reload(self, ctx, *, cog: str):
        """ Command which Reloads a Module.
            Remember to use dot path. e.g: cogs.owner
        """
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except (AttributeError, ImportError) as error:
            await ctx.message.add_reaction('👎')
            await ctx.send(f'```py\nCould not reload {cog}: {type(error).__name__} - {error}\n```')
        else:
            await ctx.message.add_reaction('👌')
            await ctx.send(f'```Successfully reloaded {cog}!```')

    @commands.command(name='pull', hidden=True)
    @commands.is_owner()
    async def _pull(self, ctx, cog: str = ''):
        """ Pull github origin.
            If argument is passed, cog will be reloaded.
        """
        try:
            g = git.cmd.Git('./')
            g.pull()
        except Exception as error:
            await ctx.send(f'```py\n{type(error).__name__}: {str(error)}\n```')
            return
        if cog != '':
            try:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            except (AttributeError, ImportError) as error:
                await ctx.message.add_reaction('👎')
                await ctx.send(f'```py\n{type(error).__name__}: {str(error)}\n```')
                return
            else:
                await ctx.message.add_reaction('👌')
                await ctx.send(f'```Successfully reloaded {cog}!```')

    @commands.command(name='stop', hidden=True, aliases=['exit', 'die', 'logout'])
    @commands.is_owner()
    async def _stop(self, ctx):
        """ Stops the bot.
        """
        msg = await ctx.send('*Goodbye. I love you. Never forget me!')
        await msg.add_reaction('👋')
        await self.bot.logout()

    @commands.command(name='toggle',description='Enable or disable a command!',hidden=True)
    @commands.is_owner()
    async def _toggle(self,ctx,*,command):
        '''
        Enable or disable a command!
        '''
        command = self.bot.get_command(command)
        if command is None:
            await ctx.send('Cannot find a command with that name.')
        elif ctx.command == command:
            await ctx.send('You cannot disable this command.')
        else:
            command.enabled = not command.enabled
            ternary = 'enabled' if command.enabled else 'disabled'
            await ctx.send(f'I have {ternary} {command.qualified_name}')

def setup(bot):
    bot.add_cog(OwnerCog(bot))
