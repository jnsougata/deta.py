import os
import aiohttp
import asyncio
from src.asyncdeta import Deta, Field, Update


async def main():
    token = os.getenv('DETA_TOKEN')
    session = aiohttp.ClientSession()
    deta = Deta(project_key=token, session=session)
    base = deta.base(name='123TEST')
    await base.add_field(key='12345678', field=Field('YOUTUBE', {}), force=True)
    await session.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
