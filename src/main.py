import os
import aiohttp
import asyncio
from asyncdeta import Deta, Field, Update


async def main():
    token = os.getenv('DETA_TOKEN')
    session = aiohttp.ClientSession()
    deta = Deta(project_key=token, session=session)
    base = deta.base(name='123TESTT')
    await session.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
