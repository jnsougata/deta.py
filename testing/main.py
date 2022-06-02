import os
import asyncio
from src.asyncdeta import Deta, Field
import time


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    base = deta.base(name='123BASE')
    keys = [f'TARGET{i}' for i in range(1000)]
    s = time.perf_counter()
    print(await base.delete_many(keys))
    e = time.perf_counter()
    await deta.close()
    print(f'Time taken {e - s:.2f} seconds to delete {len(keys)} items')


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
