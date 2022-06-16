import os
import asyncio
from src.asyncdeta import Deta, Field, Query
from tabulate import tabulate


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    base = deta.base("01PIXEL")
    drive = deta.drive("PixeL_@11223344")
    print(await base.fetch_all())
    print(await drive.files())
    await deta.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
