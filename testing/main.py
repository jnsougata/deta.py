import os
import asyncio
from src.asyncdeta import Deta, Field


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    drive = deta.drive(name='123_drive')
    base = deta.base(name='123_base')
    await base.put(key='test', field=Field(name='abc', value={'a': 1, 'b': 2}))
    await drive.upload(file_name='song.mp3', local_path='/home/jnsougata/Downloads/song.mp3')
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
