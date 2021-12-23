from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union, Optional
import nextcord

from .base import DatabaseChecker

if TYPE_CHECKING:
    from nextcord.ext import commands


@dataclass
class InviteAccount:
    """
    Represents an InviteAccount.
    """

    invite_tracker: InviteTracker
    member: nextcord.Member

    async def get_invited_users(self):
        return await self.invite_tracker.get_members_invited(
            self.member, self.member.guild
        )


class InviteTracker(DatabaseChecker):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            [
                {
                    "guild": "snowflake",
                    "member": "snowflake",
                    "members_invited": "string",
                }
            ],
            ["invites"],
        )
        self.bot = bot
        self.cache = {}

        self.bot.loop.create_task(self.__initialize_cache())

        self.bot.add_listener(self.__cleanup_guild_cache, "on_guild_remove")
        self.bot.add_listener(self.__update_guild_cache, "on_guild_add")
        self.bot.add_listener(self.__track_invite, "on_invite_create")
        self.bot.add_listener(self.__cleanup_invite, "on_invite_delete")

    async def get_invite(self, member: nextcord.Member) -> Optional[nextcord.Invite]:
        for inv in await member.guild.invites():
            for invite in self.cache[member.guild.id]:
                if invite.revoked:
                    self.cache[invite.guild.id].remove(invite)
                    return

                if invite.code == inv.code and inv.uses - invite.uses == 1:
                    await self.__update_guild_cache(member.guild)
                    return inv

    @DatabaseChecker.uses_database
    async def get_members_invited(
        self, user: Union[nextcord.User, nextcord.Member], guild: nextcord.Guild
    ):
        invited_members = await self.database.select(
            self.tables["invites"],
            ["members_invited"],
            {"guild": guild.id, "member": user.id},
        )

        if not invited_members:
            return []

        invited_members = invited_members["members_invited"]
        if isinstance(invited_members, str):
            return [
                int(invited_member)
                for invited_member in invited_members.split("\0")
                if invited_member
            ]

    async def fetch_inviter(
        self, invite: nextcord.Invite
    ) -> Union[nextcord.Member, nextcord.User]:
        inviter = invite.guild.get_member(invite.inviter.id)
        return inviter if inviter else await self.bot.get_user(invite.inviter.id)

    @DatabaseChecker.uses_database
    async def register_invite(
        self,
        invite: nextcord.Invite,
        member: nextcord.Member,
        inviter: Union[nextcord.Member, nextcord.User],
    ) -> None:
        invited_members = await self.get_members_invited(inviter, invite.guild)
        if member.id in invited_members:
            return

        invited_members.append(member.id)
        invited_members_sql = "\0".join(
            str(invited_member) for invited_member in invited_members
        )

        await self.database.updateorinsert(
            self.tables["invites"],
            {"members_invited": invited_members_sql},
            {"guild": invite.guild.id, "member": inviter.id},
            {
                "guild": invite.guild.id,
                "member": inviter.id,
                "members_invited": invited_members_sql,
            },
        )

    async def __initialize_cache(self) -> None:
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            try:
                self.cache[guild.id] = await guild.invites()
            except nextcord.Forbidden:
                pass

    async def __update_guild_cache(self, guild: nextcord.Guild) -> None:
        try:
            self.cache[guild.id] = await guild.invites()
        except nextcord.Forbidden:
            pass

    async def __track_invite(self, invite: nextcord.Invite) -> None:
        self.cache[invite.guild.id].append(invite)

    async def __cleanup_invite(self, invite: nextcord.Invite) -> None:
        if invite in self.cache[invite.guild.id]:
            self.cache[invite.guild.id].remove(invite)

    async def __cleanup_guild_cache(self, guild: nextcord.Guild) -> None:
        self.cache.pop(guild.id)

    @DatabaseChecker.uses_database
    def get_user_info(self, member: nextcord.Member) -> InviteAccount:
        return InviteAccount(self, member)
