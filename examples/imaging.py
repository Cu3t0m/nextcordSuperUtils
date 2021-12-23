import nextcord
from nextcord.ext import commands

import nextcordSuperUtils

bot = commands.Bot(command_prefix="-", intents=nextcord.Intents.all())
ImageManager = nextcordSuperUtils.ImageManager()


@bot.event
async def on_ready():
    print("Image manager is ready.", bot.user)


@bot.command()
async def test_welcome(ctx):
    member = ctx.author

    await ctx.send(
        file=await ImageManager.create_welcome_card(
            member,
            nextcordSuperUtils.Backgrounds.GAMING,
            f"Welcome, {member} 🔥",
            "Welcome to ?,! Please read the #rules.",
            title_color=(127, 255, 0),
            description_color=(127, 255, 0),
            transparency=127,
        )
    )


bot.run("token")
