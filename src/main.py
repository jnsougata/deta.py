import os
import aiohttp
import asyncio
from asyncdeta import Deta, Field, Update, dict_to_field


async def main():
    token = os.getenv('DETA_TOKEN')
    session = aiohttp.ClientSession()
    deta = Deta(project_key=token, session=session)
    base = deta.base(name='123TESTT')
    up = await base.update(key='1234567890', updates=[
        Update.set([Field('PINGROLE', '1234567890')]),
    ])
    print(up)
    await session.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
