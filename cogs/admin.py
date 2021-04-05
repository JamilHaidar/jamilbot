from itertools import count
import sqlite3
import discord
from discord.ext.commands.core import check, guild_only
from pandas.core.frame import DataFrame
import config as c
import asyncio
from io import BytesIO
from discord.ext import commands
from cogs.utils import rules,users
from cogs.utils import loops
import datetime
import pandas as pd
from cogs.utils import checks
class AdminCog(commands.Cog, name="Admin"):
    """ AdminCog """

    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.attendance_data = dict()
        self.tasks = dict()
        self.muted_members = dict()
    
    @commands.command(name='update_users',dev=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _update_users(self,ctx):
        await ctx.send('Updating database.')
        members = set([row[0] for row in users.get_table()])
        counter = 0
        for member in ctx.guild.members:
            if member not in members:
                counter+=1
                users.set_val(member.id,'current_warnings',0,ctx.guild.id)
        await ctx.send(f'Updated {counter} new members.')
    @commands.command(name='start_class',dev=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _start_class(self,ctx):
        if ctx.guild.id in self.tasks:
            await ctx.send('Class already started!')
            return
        if ctx.author.voice is None:
            await ctx.send('Please join a voice channel first!')
        else:
            channel = ctx.author.voice.channel
            await channel.connect()
            try:
                for member in ctx.guild.members:    
                    if member.bot:continue
                    if not(member.voice is None):
                        if not(member.voice.channel is None):
                            await member.move_to(channel=channel, reason='Class started.')
                    # else:
                    #     print('sending',member.nick,member.name)
                    #     await member.send('Class is starting! ')
                    #     print('dm sending',member.nick,member.name)
                    #     invitation = await channel.create_invite(max_uses=1,max_age=7200,reason='Class starting.')
                    #     dm = await member.create_dm()
                    #     await dm.send(invitation)
                    #     print('done sending',member.nick,member.name)
            except Exception as e:
                print('error!!')
                print(e)
            self.attendance_data[ctx.guild.id] = [pd.DataFrame(),channel.id]
            margs = {
            'seconds': 15,
            'minutes': 0,
            'hours': 0,
            'count': None,
            'reconnect': True,
            'loop': None
            }
            mLoop = loops.Loop(self.attendance, **margs)
            self.tasks[ctx.guild.id] = mLoop
            self.tasks[ctx.guild.id].start(guild_id=ctx.guild.id)
    
    @commands.command(name='end_class',dev=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _end_class(self,ctx):
        if ctx.guild.id not in self.tasks:
            await ctx.send('Class not started yet!')
            return
        task = self.tasks.pop(ctx.guild.id)
        task.stop()

        df = self.attendance_data[ctx.guild.id][0].fillna(0)
        total = df.sum()
        total.name = 'Total'
        df = df.append(total)
        percentage = total/(df.shape[0]-1)
        percentage.name = 'Percentage'
        percentage = percentage.apply('{:.0%}'.format)
        df = df.append(percentage)
        with BytesIO() as excel_binary:
            df.to_excel(excel_binary)
            excel_binary.seek(0)
            await ctx.send(file=discord.File(fp=excel_binary, filename=f'attendance-{datetime.datetime.now().date()}.xlsx'))

        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        for member in ctx.guild.members:
            if member.bot:continue
            if not(member.voice is None):
                if not(member.voice.channel is None):
                    await member.move_to(channel=None,reason='Class ended.')
            # else:
            #     dm = await member.create_dm()
            #     await dm.send('Class ended.')

        if not(vc is None):
            invites = await vc.channel.invites()
            for invite in invites:
                await invite.delete(reason='Class ended. Removing all invites.')
            await vc.disconnect()
  
    async def do_attendance(self,guild_id: int):
        guild = self.bot.get_guild(guild_id)
        channel_members = guild.get_channel(self.attendance_data[guild_id][1]).members
        channel_members = [elem.name +' - '+elem.nick if elem.nick is not None else elem.name for elem in channel_members]
        self.attendance_data[guild_id][0].loc[datetime.datetime.now(),channel_members]=1.0 
    
    async def attendance(self,guild_id: int):
        async with self.lock:
            await self.do_attendance(guild_id)
    
    @commands.command(name='spam', hidden=True)
    @commands.has_permissions(manage_messages=True)
    @checks.is_dev()
    async def _spam(self, ctx, times: int = 1, *, msg: str = 'spam'):
        """ Repeat a message multiple times.
        """
        for i in range(times):
            await ctx.send(msg)

    @commands.command(name='pin')
    @commands.has_permissions(manage_messages=True)
    @checks.is_dev()
    async def _pin(self, ctx):
        """ Pin previous message.
        """
        async for message in ctx.channel.history():
            passer = False
            for fix in c.prefixes:
                if message.content == f'{fix}pin':
                    passer = True
            if passer:
                continue
            await message.pin()
            return

    @commands.command(name='unpin')
    @commands.has_permissions(manage_messages=True)
    @checks.is_dev()
    async def _unpin(self, ctx):
        """ Unpin previous message.
        """
        async for message in ctx.channel.history():
            passer = False
            for fix in c.prefixes:
                if message.content == f'{fix}unpin':
                    passer = True
            if passer:
                continue
            await message.unpin()
            return

    @commands.command(name='purge')
    @commands.has_permissions(manage_guild=True)
    @checks.is_dev()
    async def _purge(self, ctx, amount: str, member: discord.Member = None, channel: int = None):
        """ Purge messages from current channel
        """
        def _member_check(m):
            return m.author == member

        if not str(amount) == 'all':
            amnt: int = int(float(amount))
        else:
            is_owner = await ctx.bot.is_owner(ctx.author)
            if not is_owner:
                await ctx.send(f'```Sorry {ctx.message.author.name}, you need to be the bot owner to run this command!```')
                return
            else:
                try:
                    channel = ctx.message.channel
                    await ctx.send(f'Are you sure? This will delete **ALL** messages in the current channel. (*{channel.name}*)\nSend **yes** to proceed.')

                    def check(m):
                        return m.content == 'yes' and m.channel == channel
                    def c_check(m):
                        return m.content == 'c' or m.content == 'cancel' and m.channel == channel

                    msg = await self.bot.wait_for('message', check=check, timeout=10)
                    await channel.send('Purging **ALL** messages from current channel in **7 seconds**!\nType \'**cancel**\' or \'**c**\' to cancel.')

                    try:
                        msg = await self.bot.wait_for('message', check=c_check, timeout=7)
                        await ctx.send('Message purge cancelled.')
                    except Exception:
                        await ctx.message.channel.purge(check=_member_check)
                except Exception:
                    await ctx.send('Response timed out, not doing anything.')
                    return
            return

        amnt += 1
        _suffix = ''
        ch = ctx.message.channel
        if channel is not None:
            ch = self.bot.get_channel(channel)
        if member is not None:
            deleted = await ch.purge(limit=amnt, check=_member_check)
            _suffix = f' from {member.name}'
        else:
            deleted = await ch.purge(limit=amnt)
        _s: str = '' if len(deleted)-1 == 1 else 's'
        msg = await ch.send(f'```Deleted {len(deleted)-1} message{_s}{_suffix}.```')
        await asyncio.sleep(1)
        await msg.delete()

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _kick(self, ctx, *members: discord.Member):
        """ Kicks the specified member(s).
        """
        for member in members:
            await ctx.message.guild.kick(member)
            await ctx.send(f'```{member} was kicked from the server.```')


    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _ban(self, ctx, *members: discord.Member):
        """ Bans the specified member(s) and deletes their messages.
        """
        for member in members:
            await ctx.message.guild.ban(member, delete_message_days=7)
            await ctx.send(f'```{member} was banned from the server.```')

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _unban(self, ctx, *, name: str):
        """ Unbans a member.
        """
        bans = await ctx.message.guild.bans()
        member = discord.utils.get(bans, user__name=name)
        if member:
            await ctx.message.guild.unban(member.user)
            await ctx.send(f'{member.user.name}#{member.user.discriminator} was unbanned. Welcome back!')
            return
        await ctx.send(f'{name} isn\' banned.')

    @commands.command(name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True, kick_members=True, ban_members=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _leave(self, ctx):
        """ Remove bot from server.
        """
        server = ctx.message.guild
        await server.leave()
    
    @commands.command(name='mute', aliases=['timeout'])
    @commands.has_permissions(manage_guild=True, kick_members=True, ban_members=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _mute(self,ctx, member: discord.Member):
        role = discord.utils.get(member.server.roles, name='Muted')
        if role is None:
            await ctx.send('Role ```Muted``` does not exist!')
            return
        try:
            self.muted_members[member.id] = member.roles[0]
        except:
            self.muted_members[member.id] = member.roles[1]

        await ctx.add_roles(member, role)
        embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        await ctx.send(embed=embed)
    
    @commands.command(name='unmute', aliases=['forgive'])
    @commands.has_permissions(manage_guild=True, kick_members=True, ban_members=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _unmute(self,ctx, member: discord.Member):
        await ctx.add_roles(member, self.muted_members.pop(member.id))
        embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        await ctx.send(embed=embed)
     
    @commands.command(name='nick', aliases=['nickname', 'changenick'])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @checks.is_dev()
    async def _nickname(self, ctx, nickname, *members: discord.Member):
        """ Change member(s) nickname(s).
        """
        for member in members:
            await member.edit(nick=nickname)

    @_nickname.error
    async def nickname_error(self, ctx, error):
        await ctx.send('Command not fully implemented yet!')

    @commands.command(name='setrule', aliases=['gamerule'])
    @commands.guild_only()
    @checks.is_dev()
    async def _setrule(self, ctx, key: str, value: str = 'get'):
        """ Set a server-side rule.
            Set value to NONE to delete server-rule.
            Valid rules:
              - prefixless: True *
              - dad: True *
              - self-harm: True *
              - warning_threshold: 3 *
        """
        key = key.lower()
        await ctx.send(rules.setrule(key, value, ctx.message.guild.id))
    
    @commands.command(name='getrule')
    @commands.guild_only()
    @checks.is_dev()
    async def _getrule(self, ctx, key: str):
        """ Get a server-side rule.
        """
        key = key.lower()
        ruleinf = rules.getrule(key, ctx.message.guild.id)
        if not ruleinf:
            await ctx.send('```apache\nNot set.```')
        else:
            await ctx.send(f'```apache\n{ruleinf}```')
    
    @commands.command(name='set_user_val')
    @commands.guild_only()
    @checks.is_dev()
    async def _set_user_val(self,ctx, member: str='',key: str='', value: int = 0):
        """ Set a server-side user value.
            Set value to 0 or leave as-is to clear that value.
            Valid keys:
                - total_warnings: 0 *
                - current_warnings: 0 *
        """
        try:
            member = await discord.ext.commands.UserConverter().convert(ctx, member)
        except discord.ext.commands.BadArgument:
            await ctx.send(f'Could not find user {member}.')
            return
        keys = ['total_warnings','current_warnings']
        key = key.lower()
        if key not in keys:
            await ctx.send(f'{key} is not a valid key.')
        else:
            val = users.set_val(member.id, key, value, ctx.message.guild.id)
            if val is False:
                await ctx.send('```apache\nNot set.```')
            return await ctx.send(f'```apache\n{val}```')
    
    @commands.command(name='get_user_val')
    @commands.guild_only()
    @checks.is_dev()
    async def _get_user_val(self,ctx, member: str='',key: str=''):
        """ Get a server-side user value.
            Valid keys:
                - total_warnings: 0 *
                - current_warnings: 0 *
        """
        try:
            member = await discord.ext.commands.UserConverter().convert(ctx, member)
        except discord.ext.commands.BadArgument:
            await ctx.send(f'Could not find user {member}.')
            return
        keys = ['total_warnings','current_warnings']
        key = key.lower()
        if key not in keys:
            await ctx.send(f'{key} is not a valid key.')
            return
        val = users.get_val(member.id,key, ctx.message.guild.id)
        if val is False:
            await ctx.send('```apache\nNot set.```')
        else:
            await ctx.send(f'```apache\n{val}```')

    @commands.command(name='get_member',aliases=['warn_history'])
    @commands.guild_only()
    @checks.is_dev()
    async def _get_member(self,ctx, member: str=''):
        '''
        Get the warning history of a specific member.
        '''
        try:
            member = await discord.ext.commands.UserConverter().convert(ctx, member)
        except discord.ext.commands.BadArgument:
            await ctx.send(f'Could not find user {member}.')
            return
        val = users.get_member(member.id,ctx.message.guild.id)
        if val is False:
            await ctx.send('```apache\nMember values never set.```')
        else:
            await ctx.send('Member: '+str(member.name)+'\nTotal warnings: '+str(val[0])+'\nCurrent warnings: '+str(val[1]))

    @commands.command(name='increment_user_val',aliases=['warn'])
    @commands.guild_only()
    @checks.is_dev()
    async def _increment_user_val(self,ctx, member: str='',key: str='current_warnings'):
        """ Warn a student.
            Valid keys:
                - total_warnings: 0 *
                - current_warnings: 0 *
            Default key:
                - current_warnings
        """
        try:
            member = await discord.ext.commands.UserConverter().convert(ctx, member)
        except discord.ext.commands.BadArgument:
            await ctx.send(f'Could not find user {member}.')
            return
        if key =='current_warnings':
            val = users.get_val(member.id,key,ctx.message.guild.id)
            if val is False:
                await ctx.send('```apache\nNot set.```')
            else:
                ruleinf = rules.getrule('warning_threshold', ctx.message.guild.id)
                if ruleinf is False:
                    await ctx.send('```apache\nwarning_threshold not set.```')
                else:
                    try:
                        ruleinf = int(ruleinf)
                    except:
                        await ctx.send(f'```apache\nwarning_threshold is not an integer ({ruleinf}).```')
                        return
                    if val >= ruleinf:
                        await ctx.send(f'{member} reached {ruleinf} warnings. Muting.')
                        users.increment_val(member.id,'total_warnings',ctx.message.guild.id)
                        users.set_val(member.id,'current_warnings',0,ctx.message.guild.id)
                        await self._mute(member)
                        await self._get_member(member.name)
                    else:
                        await ctx.send(f'{member} has {val} warnings. Incrementing.')
                        users.increment_val(member.id,'total_warnings',ctx.message.guild.id)
                        users.increment_val(member.id,'current_warnings',ctx.message.guild.id)
                        await self._get_member(member.name)
                    
                
        else:
            val = users.increment_val(member=member.id,key=key,guildId=ctx.message.guild.id)
            if val is False:
                await ctx.send('```apache\nNot set.```')
            else:
                await self._get_member(member.name)

    @commands.command(name='backup',aliases=['export','save_userdata'])
    @commands.guild_only()
    @checks.is_dev()
    async def _save_userdata(self,ctx):
        conn = sqlite3.connect('users.db')
        df = pd.read_sql_query("SELECT * FROM users", conn)
        df['member'] = [await ctx.guild.fetch_member(member).name for member in df['member']]
        with BytesIO() as excel_binary:
            df.to_excel(excel_binary)
            excel_binary.seek(0)
            await ctx.send(file=discord.File(fp=excel_binary, filename=f'userdata-{datetime.datetime.now().date()}.xlsx'))
        
    @commands.command()
    @commands.guild_only()
    @checks.is_dev()
    async def join_vc(self,ctx):
        if ctx.author.voice is None:
            await ctx.send('Please join a voice channel first!')
        else:
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command()
    @commands.guild_only()
    @checks.is_dev()
    async def leave_vc(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    @commands.guild_only()
    @checks.is_dev()
    async def clear(self,ctx,amount=5):
        await ctx.channel.purge(limit=amount+1)

def setup(bot):
    bot.add_cog(AdminCog(bot))
