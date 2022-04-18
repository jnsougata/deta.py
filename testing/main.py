import os
import aiohttp
import asyncio
from src.asyncdeta import Deta, Field, Update



async def main():
    token = os.getenv('DETA_TOKEN')
    session = aiohttp.ClientSession()
    deta = Deta(project_key=token)
    await deta.connect()
    try:
        base = deta.base(name='123TEST')
        await base.add_field(key='12345678', field=Field('YOUTUBE', ['ABC']), force=True)
    except Exception as e:
        print(e)
    finally:
        await deta.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
