# deta.py

An async library to interact with deta base & drive.

## Community
- [Discord](https://discord.gg/bh99VTt9dH)

# Table of Contents
- [Table of Contents](#table-of-contents)
- [Installing](#installation)
- [Quick Start](#quick-start)
- [Async Context Manager](#async-context-manager)

# Installation

> Python 3.8+ recommended

```shell
pip install git+https://github.com/jnsougata/deta.py
```

# Quick Start

```python
import deta
import asyncio


async def main():
  service = deta.Deta(DETA_PROJECT_KEY)

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
  stream = await drive.get('song.mp3')
  async for chunk, _ in stream.iter_chunks():
    # do something with the chunk
    ...

    # or read the entire file
    content = await stream.read()
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
    async with deta.Deta(DETA_PROJECT_KEY) as service:
        base = service.base('TEST_BASE')
        print(await base.get())

        drive = service.drive('TEST_DRIVE')
        stream = await drive.get('song.mp3')
        with open('song.mp3', 'wb') as f:
            f.write(await stream.read())
```
# Documentation
Read the [documentation](https://deta.readthedocs.io/en/latest/) for more information.
