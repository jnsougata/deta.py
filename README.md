# deta

An async library to interact with deta.sh base & drive

- [Discord](https://discord.gg/bh99VTt9dH)
- [GitHub](https://github.com/jnsougata)

# Table of Contents
- [deta](#deta)
- [Table of Contents](#table-of-contents)
- [Installing](#installing)
- [Quick Start](#quick-start)
- [Async Context Manager](#async-context-manager)
- [Usage](#usage)
- [Base](#base)
- [Drive](#drive)
- [Records](#records)
- [Queries](#queries)
- [Updates](#updates)

# Installing

**Recommended:** Python 3.8.0 or higher

```shell
pip install git+https://github.com/jnsougata/deta
```

# Quick Start

```python
import asyncio
from deta import Deta, Record


async def main():
  deta = Deta()

  # instantiating a base
  base = deta.base(name='TEST_BASE')

  # instantiating a drive
  drive = deta.drive(name='TEST_DRIVE')

  # put single json deta base
  await base.put(
    Record({'name': 'John Doe', 'age': 20}, key='xyz', expire_after=100)
  )

  # or put multiple records with a single request
  await base.put(
    Record({'name': 'John Doe 0', 'age': 20}, key='xyz_1', expire_after=100),
    Record({'name': 'John Doe 1', 'age': 21}, key='xyz_2', expire_after=100),
    Record({'name': 'John Doe 2', 'age': 22}, key='xyz_3', expire_after=100)
  )

  # doing queries
  q = deta.Query()
  q.equal("name", "John")
  q.equal("address.city", "New York")
  q.range("age", 18, 30)
  q.not_equal("position", "Manager")
  q.contains("id", "-")
  results = await db.fetch(q)
  print(results)

  # updating records
  u = deta.Updater()
  u.set("inactive", True)
  u.increment("age")
  u.delete("address")
  await db.update("user_777", u)

  # downloading a song stored in deta drive
  reader = await drive.get('song.mp3')
  async for chunk, _ in reader.iter_chunks():
    # do something with the chunk
    ...

  # or read the entire file
  content = await reader.read()
  # do something with the content

  # closing deta connection
  await deta.close()


if __name__ == '__main__':
  asyncio.run(main())
```

# Async Context Manager
```python
async def main():
    async with Deta() as d:

        base = d.base('TEST_BASE')
        print(await base.get())

        drive = d.drive('TEST_DRIVE')
        reader = await drive.get('song.mp3')
        content = await reader.read()
        with open('song.mp3', 'wb') as f:
            f.write(content)
```

# Usage

# Base
- `async put(*records: Record)` 
  - **Returns:** Dict[str, Any]
- `async delete(self, *keys: str)` 
  - **Returns:** Optional[List[Dict[str, str]]]
- `async get(*keys: str)`
  - **Returns:** List[Dict[str, Any]]
- `async insert(*records: Record)`
  - **Returns:** Optional[List[Dict[str, Any]]]
- `async update(key: str, updater: Updater)`
  - **Returns:** Dict[str, Any]
- `async query(*queries: Query, limit: Optional[int], last: Optional[str])`
  - **Returns:** Dict[str, Any]

# Drive
- `async put(content: os.PathLike, *, save_as: Optional[str], folder: Optional[str])`
  - **Returns:** Dict[str, Any]
- `async get(filename: str, *, range: Optional[Tuple[int, int]])`
  - **Returns:** StreamReader (Async)
- `async files(limit: Optional[int], prefix: Optional[str], last: Optional[str])`
  - **Returns:** Dict[str, Any]
- `async delete(*names: str)`
  - **Returns:** Dict[str, Any]
- `async size_of(filename: str)`
  - **Returns:** int

# Records
- Base class **Record** 
- **Args**:
  - `data: Dict[str, Any]`
- **KwArgs**:
  - `key: Optional[str]`
  - `expire_at: Optional[datetime]`
  - `expire_after: Optional[int]`

# Queries
- Base class **Query**
- Methods:
  - `equal(field: str, value: Any)`
  - `not_equal(field: str, value: Any)`
  - `contains(field: str, value: Any)`
  - `not_contains(field: str, value: Any)`
  - `greater_than(field: str, value: Any)`
  - `greater_equal(field: str, value: Any)`
  - `less_than(field: str, value: Any)`
  - `less_equal(field: str, value: Any)`
  - `prefix(field: str, value: Any)`
  - `range(field: field: str, start: float, end: float)`

# Updates
- Base class **Updater**
  - `set(field: str, value: Any)`
  - `delete(field: str)`
  - `increment(field: str, value: int)`
  - `append(field: str, value: Any)`
  - `prepend(field: str, value: Any)`
