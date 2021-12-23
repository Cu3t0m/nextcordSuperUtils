import nextcord
from nextcord.ext.commands import Bot, Context

import nextcordSuperUtils
from nextcordSuperUtils import ModMailManager

bot = Bot(command_prefix="-", intents=nextcord.Intents.all())
ModmailManager = ModMailManager(bot, trigger="-modmail")


@bot.event
async def on_ready():
    db = nextcordSuperUtils.DatabaseManager.connect(...)
    await ModmailManager.connect_to_database(db, ["modmail"])

    print("ModMailManager is ready.", bot.user)


@ModmailManager.event()
async def on_modmail_request(ctx: Context):
    guilds = await ModmailManager.get_mutual_guilds(ctx.author)
    guild = await ModmailManager.get_modmail_guild(ctx, guilds)
    channel = await ModmailManager.get_channel(guild)
    msg = await ModmailManager.get_message(ctx)
    await channel.send(msg)


@bot.command()
async def setchannel(ctx, channel: nextcord.TextChannel):
    await ModmailManager.set_channel(channel)
    await ctx.send(f"Channel set to {channel.mention} for {channel.guild}")


bot.run("token")
