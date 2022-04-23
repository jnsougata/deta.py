async-deta
==========

An async library to interact with deta.sh

- `Discord <https://discord.gg/YAFGAaMrTC>`_
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

    pip install git+https://github.com/jnsougata/async-deta

Quick Start
--------------

.. code:: py

    # interacting with deta drive & base

    import os
    import asyncio
    from asyncdeta import Deta, Field


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
        resp = await drive.download(file_name='song.mp3')
        with open('song.mp3', 'wb') as f:
            f.write(resp)

        # closing deta connection
        await deta.close()


    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())

Usage
------

Base
~~~~~~
.. csv-table::
   :header: "Method", "Return Type", "Description"
   :widths: 80, 80, 100

   "add_field(self, key: str, field: Field, force: bool = False)", "Dict[str, Any]", "adds a field to an existing key. If field already exists, old value will be overwritten."

Drive
~~~~~~