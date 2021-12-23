from __future__ import annotations

import nextcord
from nextcord.ext import commands
from typing import Union, List, Optional

from .base import DatabaseChecker


class ModMailManager(DatabaseChecker):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], trigger: str):
        self.bot = bot
        self.trigger = trigger

        super().__init__([{"guild": "snowflake", "channel": "snowflake"}], ["modmail"])

        self.bot.add_listener(self._handle_modmail_requests, "on_message")

    async def _handle_modmail_requests(self, message: nextcord.Message):
        if not isinstance(message.channel, nextcord.DMChannel):
            return

        if message.author.id == self.bot.user.id:
            return

        if self.trigger.lower() == (message.content.split())[0].lower():
            await self.call_event(
                "on_modmail_request",
                await self.bot.get_context(message=message, cls=commands.Context),
            )

    async def set_channel(self, channel: nextcord.TextChannel) -> None:
        """
        :param channel: Channel that ModMail is sent to.
        :type channel: nextcord.TextChannel
        :return:
        :rtype: None
        """

        self._check_database()

        table_data = {"guild": channel.guild.id, "channel": channel.id}

        await self.database.updateorinsert(
            self.tables["modmail"], table_data, {"guild": channel.guild.id}, table_data
        )

    async def get_channel(self, guild: nextcord.Guild) -> nextcord.TextChannel:
        """
        :param guild: The guild to fetch the ModMail Channel object for
        :type guild: nextcord.Guild
        :return:
        :rtype: nextcord.TextChannel
        """

        channel_id = await self.database.select(
            self.tables["modmail"], ["channel"], {"guild": guild.id}, fetchall=False
        )
        return self.bot.get_channel(channel_id["channel"])

    async def get_mutual_guilds(self, user: nextcord.User) -> List[nextcord.Guild]:
        """
        :param user: User to fetch the mutual guilds with the bot.
        :type user: nextcord.User
        :return:
        :rtype: List[nextcord.Guild]
        """

        return [x for x in self.bot.guilds if nextcord.utils.get(x.members, id=user.id)]

    async def get_modmail_guild(
        self, ctx: commands.Context, guilds: List[nextcord.Guild]
    ) -> Optional[nextcord.Guild]:
        """
        :param ctx: Used to fetch channel
        :type ctx: commands.Context
        :param guilds: List of all mutual guilds
        :type guilds: List[nextcord.Guild]
        :return:
        :rtype: nextcord.Guild
        """
        embed = nextcord.Embed(
            title="ModMail",
            description="Please type the Guild ID to send modmail to that server",
        )
        for guild in guilds:
            embed.add_field(name=f"{guild}", value=f"{guild.id}")

        def check(message):
            if isinstance(message.channel, nextcord.DMChannel):
                return message.author.id == ctx.author.id

        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=60)

        guildids = [guild.id for guild in guilds]

        if int(msg.content) in guildids:
            return self.bot.get_guild(int(msg.content))
        return None

    async def get_message(self, ctx: commands.Context) -> str:
        """
        :param ctx: fetch channel
        :type ctx: commands.Context
        :return:
        :rtype: str
        """

        embed = nextcord.Embed(
            title="ModMail", description="Please type your message to the Mods."
        )
        await ctx.send(embed=embed)

        def check(message):
            if isinstance(message.channel, nextcord.DMChannel):
                return message.author.id == ctx.author.id

        msg = await self.bot.wait_for("message", check=check, timeout=60)
        return msg.content
