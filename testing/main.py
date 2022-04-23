import os
import asyncio
from src.asyncdeta import Deta, Field


async def main():
    deta = Deta(os.getenv("PROJECT_KEY"))
    await deta.connect()
    drive = deta.drive(name='test_123')
    base = deta.base(name='test_123')
    await base.put(key='test', field=Field(name='abc', value={'a': 1, 'b': 2}))
    resp = await drive.download(file_name='song.mp3')
    with open('song.mp3', 'wb') as f:
        f.write(resp)
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
