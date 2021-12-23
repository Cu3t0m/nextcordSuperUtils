import nextcord
from nextcord.ext import commands

import nextcordSuperUtils

bot = commands.Bot(command_prefix="-", intents=nextcord.Intents.all())
ReactionManager = nextcordSuperUtils.ReactionManager(bot)


@ReactionManager.event()
async def on_reaction_event(guild, channel, message, member, emoji):
    """This event will be run if there isn't a role to add to the member."""

    if ...:
        print("Created ticket.")


@bot.event
async def on_ready():
    database = nextcordSuperUtils.DatabaseManager.connect(...)
    await ReactionManager.connect_to_database(database, ["reaction_roles"])

    print("Reaction manager is ready.", bot.user)


@bot.command()
async def reaction(
    ctx, message, emoji: str, remove_on_reaction, role: nextcord.Role = None
):
    message = await ctx.channel.fetch_message(message)

    await ReactionManager.create_reaction(
        ctx.guild, message, role, emoji, remove_on_reaction
    )


bot.run("token")
