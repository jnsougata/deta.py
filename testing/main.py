import asyncio
import os

from src.asyncdeta import Deta


async def main():
    deta = Deta(os.getenv("PROJECT_KEY"))
    await deta.connect()
    drive = deta.drive(name='test_123')
    resp = await drive.download(file_name='song.mp3')
    with open('song.mp3', 'wb') as f:
        f.write(resp)
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
