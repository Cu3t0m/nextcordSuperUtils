import nextcordSuperUtils
import asyncio


async def fivem_test():
    fivem_server = await nextcordSuperUtils.FiveMServer.fetch(
        ...
    )  # Replace ... by the IP (port is needed!)
    # e.g. localhost:30120

    print(fivem_server)


asyncio.run(fivem_test())
