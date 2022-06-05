import os
import asyncio
from src.asyncdeta import Deta, Field, Query
from tabulate import tabulate


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    base = deta.base(name='01PIXEL')
    q = await base.query([Query.equal('RECEPTION', '857943375558082570')])
    print(q)
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
