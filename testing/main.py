import os
import asyncio
from src.asyncdeta import Deta, Field
from tabulate import tabulate


async def main():
    deta = Deta(os.getenv("DETA_TOKEN"))
    await deta.connect()
    base = deta.base(name='01PIXEL')
    payload = await base.fetch_all()
    tables = [tabulate(data.items(), headers='keys') for data in payload]
    ini = '\n'.join(tables)
    with open('table.pxl', 'w') as f:
        f.write(ini)
    await deta.close()


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
