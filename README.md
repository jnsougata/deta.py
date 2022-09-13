# deta

An async library to interact with deta.sh base & drive

- [Discord](https://discord.gg/bh99VTt9dH)
- [GitHub](https://github.com/jnsougata)

# Table of Contents
- [Installation](#installing)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Base](#base)
- [Drive](#drive)

# Installing

**Python 3.6 or higher is required**

```shell
pip install git+https://github.com/jnsougata/deta
```

# Quick Start

```python
import os
import asyncio
from deta import Deta, Field


async def main():

    deta = Deta()

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
```

# Usage

# Base
- `add_field(key: str, field: Field, force: bool = False)` 
  - **Returns:** Dict[str, Any]
- `remove_field(self, key: str, field_name: str)` 
  - **Returns:** Dict[str, Any]
- `fetch(key: str)`
  - **Returns:** Dict[str, Any]
- `fetch_by_keys(*keys: str)` 
  - **Returns:** List[Dict[str, Any]]
- `everything()`
  - **Returns:** List[Dict[str, Any]]
- `put(key: str, field: Field, *, expire_at: datetime = None, expire_after: Union[int, float] = None)`
  - **Returns:** Dict[str, Any]
- `put_many(key: str, fields: List[Field], *, expire_at: datetime = None, expire_after: Union[int, float] = None)` 
  - **Returns:** Dict[str, Any]
- `put_bulk(key: str, fields: List[List[Field]], *, expire_ats: List[datetime] = None, expire_afters: List[Union[int, float]] = None)`
  - **Returns:** List[Dict[str, Any]]
- `insert(key: str, field: Field)`
  - **Returns:** Dict[str, Any]
- `insert_many(key: str, fields: List[Field])`
  - **Returns:** Dict[str, Any]
- `update(key: str, updates: List[Update])`
  - **Returns:** Dict[str, Any]
- `delete(*keys: str)`
  - **Returns:** Dict[str, Any]

# Drive
- `files(limit: int = None, prefix: str = None)`
  - **Returns:** List[Dict[str, Any]]
- `delete(*names: str)`
  - **Returns:** Dict[str, Any]
- `upload(content: [str | bytes], name: str)` 
  - **Returns:** Dict[str, Any]
- `get(name: str)`
  - **Returns:** io.BytesIO"
