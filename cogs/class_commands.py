import discord
from discord.ext import commands

class ClassCommands(commands.cog):

    def __init__(self, client) :
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online.')

    @commands.command()
    async def ping(self,ctx):
        await ctx.send('Pong!')

def setup(client):
    client.add_cog(ClassCommands(client))
