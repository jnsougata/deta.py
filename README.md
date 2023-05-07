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
import deta
import asyncio


async def main():
  service = deta.Deta()

  # instantiating a base
  base = service.base(name='TEST_BASE')

  # instantiating a drive
  drive = service.drive(name='TEST_DRIVE')

  # put single json deta base
  await base.put(
    deta.Record({'name': 'John Doe', 'age': 20}, key='xyz', expire_after=100)
  )

  # or put multiple records with a single request
  await base.put(
    deta.Record({'name': 'John Doe 0', 'age': 20}, key='xyz_1', expire_after=100),
    deta.Record({'name': 'John Doe 1', 'age': 21}, key='xyz_2', expire_after=100),
    deta.Record({'name': 'John Doe 2', 'age': 22}, key='xyz_3', expire_after=100)
  )

  # doing queries
  q = deta.Query()
  q.equals("name", "John")
  q.equals("address.city", "New York")
  q.range("age", 18, 30)
  q.not_equals("position", "Manager")
  q.contains("id", "-")
  results = await base.fetch([q])
  print(results)

  # updating records
  u = deta.Updater()
  u.set("inactive", True)
  u.increment("age")
  u.delete("address")
  await base.update("user_777", u)

  # downloading a song stored in deta drive
  result = await drive.get('song.mp3')
  if result.ok:
    async for chunk, _ in result.reader.iter_chunks():
      # do something with the chunk
      ...

    # or read the entire file
    content = await result.read()
    # do something with the content

  # closing deta connection
  await service.close()


if __name__ == '__main__':
  asyncio.run(main())
```

# Async Context Manager
```python
import deta

async def main():
    async with deta.Deta() as service:
        base = service.base('TEST_BASE')
        print(await base.get())

        drive = service.drive('TEST_DRIVE')
        result = await drive.get('song.mp3')
        content = await result.read()
        with open('song.mp3', 'wb') as f:
            f.write(content)
```

# Usage

# Base
- `async put(*records: Record)` 
  - **Returns:** List[Result]
- `async delete(*keys: str)` 
  - **Returns:** List[Result]
- `async get(*keys: str)`
    - **Returns:** List[Result]
- `async insert(*records: Record)`
  - **Returns:** List[Result]
- `async update(key: str, updater: Updater)`
  - **Returns:** Result
- `async fetch(queries: List[Query], limit: Optional[int], last: Optional[str])`
  - **Returns:** Result
- `async fetch_until_end(queries: List[Query])`
  - **Returns:** List[Result]

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
  - `equals(field: str, value: Any)`
  - `not_equals(field: str, value: Any)`
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
