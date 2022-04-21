import os
import asyncio
from src.asyncdeta import Deta, Field


async def main():
    deta = Deta('abc_xyz')
    await deta.connect()
    base = deta.base(name='123TEST')
    await base.add_field(key='12345678', field=Field('YOUTUBE', '123'), force=True)
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
