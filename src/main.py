import os
import aiohttp
import asyncio
from asyncdeta import Deta, Field, Updater


async def main():
    token = os.getenv('DETA_TOKEN')
    session = aiohttp.ClientSession()
    deta = Deta(project_key=token, session=session)
    base = deta.base(name='GUILD193978189532364801')
    print(base.get('arole'))
    await base.cache()
    print(base.get('arole'))
    await session.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
