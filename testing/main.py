import os
import asyncio
from src.asyncdeta import Deta, Field, Query


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    base = deta.base("01PIXEL")
    q = await base.query(Query.primary_key(prefix='1'))
    print(q)
    print(await base.fetch_all())
    await deta.close()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
