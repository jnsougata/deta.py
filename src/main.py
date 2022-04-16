import os
import aiohttp
import asyncio
from asyncdeta import Deta, Field, Updater


async def main():
    token = os.getenv('DETA_TOKEN')
    session = aiohttp.ClientSession()
    deta = Deta(project_key=token, session=session)
    base = deta.base(name='123TEST')
    await base.update(
        key='user_100',
        data=[
            Updater.set([Field('NAME', 'HEHEHO')]),
            Updater.increment([Field('AGE', 3)]),
            Updater.remove([Field('SEX', 'Any')])
        ]
    )
    await session.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
