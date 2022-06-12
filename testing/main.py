import os
import asyncio
from src.asyncdeta import Deta, Field, Query
from tabulate import tabulate


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    base = deta.base(name='1234TEST')
    await base.put(key='exp', field=Field(name='destroy', value='This is a test'), expire_after=30)
    await base.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
