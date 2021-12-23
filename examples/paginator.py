import nextcord
from nextcord.ext import commands

import nextcordSuperUtils

bot = commands.Bot(command_prefix="-")


@bot.event
async def on_ready():
    print("Page manager is ready.", bot.user)


@bot.command()
async def paginator(ctx):
    messages = [
        nextcord.Embed(title="Data (1/2)", description="Hello world"),
        nextcord.Embed(title="Data (2/2)", description="Hello world"),
    ]

    await nextcordSuperUtils.ButtonsPageManager(ctx, messages).run()


bot.run("token")
