import asyncio
from src.asyncdeta import Deta


async def main():
    deta = Deta('c0hzr4gf_5us9rqXTgKDF4gHRXXyvUkV8GiTpQY9a')
    await deta.connect()
    drive = deta.drive(name='test_123')
    resp = await drive.upload(file_name='main.py', local_path='main.py')
    print(resp)
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
