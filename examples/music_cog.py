import nextcordSuperUtils
from nextcord.ext import commands
from nextcordSuperUtils import MusicManager


bot = commands.Bot(command_prefix="-")


class Music(commands.Cog, nextcordSuperUtils.CogManager.Cog, name="Music"):
    def __init__(self, bot):
        self.bot = bot
        # self.client_secret = ""
        # self.client_id = ""
        self.MusicManager = MusicManager(self.bot, spotify_support=False)

        # self.MusicManager = MusicManager(bot, client_id=self.client_id,
        #                                   client_secret=self.client_secret, spotify_support=True)

        # if using spotify support use this instead ^^^

        super().__init__()

    @nextcordSuperUtils.CogManager.event(nextcordSuperUtils.MusicManager)
    async def on_music_error(self, ctx, error):
        raise error  # Add error handling here

    @nextcordSuperUtils.CogManager.event(nextcordSuperUtils.MusicManager)
    async def on_play(self, ctx, player):
        await ctx.send(f"Now playing: {player}")

    @nextcordSuperUtils.CogManager.event(nextcordSuperUtils.MusicManager)
    async def on_queue_end(self, ctx):
        print(f"The queue has ended in {ctx}")
        # You could wait and check activity, etc...

    @nextcordSuperUtils.CogManager.event(nextcordSuperUtils.MusicManager)
    async def on_inactivity_disconnect(self, ctx):
        print(f"I have left {ctx} due to inactivity..")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music manager is ready.", self.bot.user)

    @commands.command()
    async def leave(self, ctx):
        if await self.MusicManager.leave(ctx):
            await ctx.send("Left Voice Channel")

    @commands.command()
    async def np(self, ctx):
        if player := await self.MusicManager.now_playing(ctx):
            duration_played = await self.MusicManager.get_player_played_duration(
                ctx, player
            )
            # You can format it, of course.

            await ctx.send(
                f"Currently playing: {player}, \n"
                f"Duration: {duration_played}/{player.duration}"
            )

    @commands.command()
    async def join(self, ctx):
        if await self.MusicManager.join(ctx):
            await ctx.send("Joined Voice Channel")

    @commands.command()
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await self.MusicManager.join(ctx)

        async with ctx.typing():
            players = await self.MusicManager.create_player(query, ctx.author)

        if players:
            if await self.MusicManager.queue_add(
                players=players, ctx=ctx
            ) and not await self.MusicManager.play(ctx):
                await ctx.send("Added to queue")

        else:
            await ctx.send("Query not found.")

    @commands.command()
    async def pause(self, ctx):
        if await self.MusicManager.pause(ctx):
            await ctx.send("Player paused.")

    @commands.command()
    async def resume(self, ctx):
        if await self.MusicManager.resume(ctx):
            await ctx.send("Player resumed.")

    @commands.command()
    async def volume(self, ctx, volume: int):
        await self.MusicManager.volume(ctx, volume)

    @commands.command()
    async def loop(self, ctx):
        is_loop = await self.MusicManager.loop(ctx)
        await ctx.send(f"Looping toggled to {is_loop}")

    @commands.command()
    async def queueloop(self, ctx):
        is_loop = await self.MusicManager.queueloop(ctx)
        await ctx.send(f"Queue looping toggled to {is_loop}")

    @commands.command()
    async def history(self, ctx):
        formatted_history = [
            f"Title: '{x.title}'\nRequester: {x.requester.mention}"
            for x in (await self.MusicManager.get_queue(ctx)).history
        ]

        embeds = nextcordSuperUtils.generate_embeds(
            formatted_history,
            "Song History",
            "Shows all played songs",
            25,
            string_format="{}",
        )

        page_manager = nextcordSuperUtils.PageManager(ctx, embeds, public=True)
        await page_manager.run()

    @commands.command()
    async def skip(self, ctx, index: int = None):
        await self.MusicManager.skip(ctx, index)

    @commands.command()
    async def queue(self, ctx):
        formatted_queue = [
            f"Title: '{x.title}\nRequester: {x.requester.mention}"
            for x in (await self.MusicManager.get_queue(ctx)).queue
        ]

        embeds = nextcordSuperUtils.generate_embeds(
            formatted_queue,
            "Queue",
            f"Now Playing: {await self.MusicManager.now_playing(ctx)}",
            25,
            string_format="{}",
        )

        page_manager = nextcordSuperUtils.PageManager(ctx, embeds, public=True)
        await page_manager.run()


bot.add_cog(Music(bot))
bot.run("token")
