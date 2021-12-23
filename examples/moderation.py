from datetime import datetime

import nextcord

import nextcordSuperUtils

bot = nextcordSuperUtils.ManagerClient(
    "token", command_prefix="-", intents=nextcord.Intents.all()
)

InfractionManager = nextcordSuperUtils.InfractionManager(bot)
BanManager = nextcordSuperUtils.BanManager(bot)
KickManager = nextcordSuperUtils.KickManager(bot)
MuteManager = nextcordSuperUtils.MuteManager(bot)

bot.managers = [InfractionManager, BanManager, MuteManager]

InfractionManager.add_punishments(
    [
        nextcordSuperUtils.Punishment(KickManager, punish_after=3),
        nextcordSuperUtils.Punishment(MuteManager, punish_after=4),
        nextcordSuperUtils.Punishment(BanManager, punish_after=5),
    ]
)


def make_removed_embeds(removed_infractions, member):
    return nextcordSuperUtils.generate_embeds(
        [
            f"**Reason: **{infraction.reason}\n"
            f"**ID: **{infraction.id}\n"
            f"**Date of Infraction: **{infraction.date_of_infraction}"
            for infraction in removed_infractions
        ],
        title=f"Removed Infractions",
        fields=25,
        description=f"List of infractions that were removed from {member.mention}.",
    )


async def make_infraction_embed(member_infractions, member):
    return nextcordSuperUtils.generate_embeds(
        [
            f"**Reason: **{await infraction.reason()}\n"
            f"**ID: **{infraction.id}\n"
            f"**Date of Infraction: **{await infraction.datetime()}"
            for infraction in member_infractions
        ],
        title=f"Infractions of {member}",
        fields=25,
        description=f"List of {member.mention}'s infractions.",
    )


@MuteManager.event()
async def on_unmute(member, reason):
    print(f"{member} has been unmuted. Mute reason: {reason}")


@BanManager.event()
async def on_unban(member, reason):
    print(f"{member} has been unbanned. ban reason: {reason}")


@BanManager.event()
async def on_punishment(ctx, member, punishment):
    await ctx.send(f"{member.mention} has been punished!")


@bot.event
async def on_ready():
    bot.database = nextcordSuperUtils.DatabaseManager.connect(...)

    print("Infraction manager is ready.", bot.user)


@bot.command()
async def mute(
    ctx,
    member: nextcord.Member,
    time_of_mute: nextcordSuperUtils.TimeConvertor,
    reason: str = "No reason specified.",
):
    try:
        await MuteManager.mute(member, reason, time_of_mute)
    except nextcordSuperUtils.AlreadyMuted:
        await ctx.send(f"{member} is already muted.")
    else:
        await ctx.send(f"{member} has been muted. Reason: {reason}")


@bot.command()
async def unmute(ctx, member: nextcord.Member):
    if await MuteManager.unmute(member):
        await ctx.send(f"{member.mention} has been unmuted.")
    else:
        await ctx.send(f"{member.mention} is not muted!")


@bot.command()
async def ban(
    ctx,
    member: nextcord.Member,
    time_of_ban: nextcordSuperUtils.TimeConvertor,
    reason: str = "No reason specified.",
):
    await ctx.send(f"{member} has been banned. Reason: {reason}")
    await BanManager.ban(member, reason, time_of_ban)


@bot.command()
async def unban(ctx, user: nextcord.User):
    if await BanManager.unban(user, guild=ctx.guild):
        await ctx.send(f"{user} has been unbanned.")
    else:
        await ctx.send(f"{user} is not banned.")


@bot.group(invoke_without_command=True)
async def infractions(ctx, member: nextcord.Member):
    member_infractions = await InfractionManager.get_infractions(member)

    await nextcordSuperUtils.PageManager(
        ctx,
        await make_infraction_embed(member_infractions, member),
    ).run()


@infractions.command()
async def add(ctx, member: nextcord.Member, reason: str = "No reason specified."):
    infraction = await InfractionManager.warn(ctx, member, reason)

    embed = nextcord.Embed(title=f"{member} has been warned.", color=0x00FF00)

    embed.add_field(name="Reason", value=await infraction.reason(), inline=False)
    embed.add_field(name="Infraction ID", value=infraction.id, inline=False)
    embed.add_field(
        name="Date of Infraction", value=str(await infraction.datetime()), inline=False
    )
    # Incase you don't like the Date of Infraction format you can change it using datetime.strftime

    await ctx.send(embed=embed)


@infractions.command()
async def get(ctx, member: nextcord.Member, infraction_id: str):
    infractions_found = await InfractionManager.get_infractions(
        member, infraction_id=infraction_id
    )

    if not infractions_found:
        await ctx.send(
            f"Cannot find infraction with id {infraction_id} on {member.mention}'s account"
        )
        return

    infraction = infractions_found[0]

    embed = nextcord.Embed(
        title=f"Infraction found on {member}'s account!", color=0x00FF00
    )

    embed.add_field(name="Reason", value=await infraction.reason(), inline=False)
    embed.add_field(name="Infraction ID", value=infraction.id, inline=False)
    embed.add_field(
        name="Date of Infraction", value=str(await infraction.datetime()), inline=False
    )
    # Incase you don't like the Date of Infraction format you can change it using datetime.strftime

    await ctx.send(embed=embed)


@infractions.command()
async def get_before(
    ctx, member: nextcord.Member, from_time: nextcordSuperUtils.TimeConvertor
):
    from_timestamp = datetime.utcnow().timestamp() - from_time

    member_infractions = await InfractionManager.get_infractions(
        member, from_timestamp=from_timestamp
    )

    await nextcordSuperUtils.PageManager(
        ctx,
        await make_infraction_embed(member_infractions, member),
    ).run()


@infractions.command()
async def clear(ctx, member: nextcord.Member):
    removed_infractions = []

    for infraction in await InfractionManager.get_infractions(member):
        removed_infractions.append(await infraction.delete())

    await nextcordSuperUtils.PageManager(
        ctx,
        make_removed_embeds(removed_infractions, member),
    ).run()


@infractions.command()
async def remove(ctx, member: nextcord.Member, infraction_id: str):
    infractions_found = await InfractionManager.get_infractions(
        member, infraction_id=infraction_id
    )

    if not infractions_found:
        await ctx.send(
            f"Cannot find infraction with id {infraction_id} on {member.mention}'s account"
        )
        return

    removed_infraction = await infractions_found[0].delete()

    embed = nextcord.Embed(
        title=f"Infraction removed from {member}'s account!", color=0x00FF00
    )

    embed.add_field(name="Reason", value=removed_infraction.reason, inline=False)
    embed.add_field(name="Infraction ID", value=removed_infraction.id, inline=False)
    embed.add_field(
        name="Date of Infraction",
        value=str(removed_infraction.date_of_infraction),
        inline=False,
    )

    await ctx.send(embed=embed)


@infractions.command()
async def remove_before(
    ctx, member: nextcord.Member, from_time: nextcordSuperUtils.TimeConvertor
):
    from_timestamp = datetime.utcnow().timestamp() - from_time

    member_infractions = await InfractionManager.get_infractions(
        member, from_timestamp=from_timestamp
    )
    removed_infractions = []

    for infraction in member_infractions:
        removed_infractions.append(await infraction.delete())

    await nextcordSuperUtils.PageManager(
        ctx,
        make_removed_embeds(removed_infractions, member),
    ).run()


bot.run(cogs_directory=None)
