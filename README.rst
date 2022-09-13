deta
==========

An async library to interact with deta.sh base & drive

- `Discord <https://discord.gg/bh99VTt9dH>`_
- `GitHub <https://github.com/jnsougata>`_

Table of Contents
=================
- `Installation <#installing>`_
- `Quick Start <#quick-start>`_
- `Usage <#usage>`_
- `Base <#base>`_
- `Drive <#drive>`_


Installing
----------

**Python 3.6 or higher is required**

.. code:: sh

    pip install git+https://github.com/jnsougata/deta

Quick Start
--------------

.. code:: py

    import os
    import asyncio
    from deta import Deta, Field


    async def main():

        deta = Deta(os.getenv("PROJECT_KEY"))

        # mandatory to assign a session
        await deta.connect()

        # instantiating a drive
        drive = deta.drive(name='test_123')

        # instantiating a base
        base = deta.base(name='test_123')

        # storing a json obj to deta base
        await base.put(key='test', field=Field(name='abc', value={'a': 1, 'b': 2}))

        # downloading a song stored in deta drive
        resp = await drive.get(file_name='song.mp3')
        with open('song.mp3', 'wb') as f:
            f.write(resp.read())

        # closing deta connection
        await deta.close()

    asyncio.run(main())

Usage
------

Base
~~~~~~
.. csv-table::
   :header: "Method", "Return Type"
   :widths: 1000, 100

   "``add_field(key: str, field: Field, force: bool = False)``", "Dict[str, Any]"
   "``remove_field(self, key: str, field_name: str)``", "Dict[str, Any]"
   "``fetch(key: str)``", "Dict[str, Any]"
   "``fetch_by_keys(*keys: str)``", "List[Dict[str, Any]]"
   "``everything()``", "List[Dict[str, Any]]"
   "``put(key: str, field: Field, *, expire_at: datetime = None, expire_after: Union[int, float] = None)``", "Dict[str, Any]"
   "``put_many(key: str, fields: List[Field], *, expire_at: datetime = None, expire_after: Union[int, float] = None)``", "Dict[str, Any]"
   "``put_bulk(key: str, fields: List[List[Field]], *, expire_ats: List[datetime] = None, expire_afters: List[Union[int, float]] = None)``", "List[Dict[str, Any]]"
   "``insert(key: str, field: Field)``", "Dict[str, Any]"
   "``insert_many(key: str, fields: List[Field])``", "Dict[str, Any]"
   "``update(key: str, updates: List[Update])``", "Dict[str, Any]"
   "``delete(*keys: str)``", "Dict[str, Any]"

Drive
~~~~~~
.. csv-table::
   :header: "Method", "Return Type"
   :widths: 1000, 100

   "``files(limit: int = None, prefix: str = None)``", "List[Dict[str, Any]]"
   "``delete(*names: str)``", "Dict[str, Any]"
   "``upload(content: [str | bytes], name: str)``", "Dict[str, Any]"
   "``get(name: str)``", "io.BytesIO"
