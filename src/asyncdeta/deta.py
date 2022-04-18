import asyncio
import aiohttp
from .base import _Base


class Deta:

    def __init__(self, *, project_key: str):
        self._session = None
        self._project_key = project_key

    async def connect(self, *, session: aiohttp.ClientSession = None, loop: asyncio.AbstractEventLoop = None):
        """
        creates a new session for Deta to make requests to the API
        """
        if session is None:
            if loop:
                self._session = aiohttp.ClientSession(loop=loop)
            else:
                self._session = aiohttp.ClientSession()
        else:
            self._session = session

    async def close(self):
        """
        closes the existing session
        """
        await self._session.close()

    def base(self, name: str) -> _Base:
        """
        creates a new instance of the Base
        """
        return _Base(name=name, deta=self)

    def drive(self):
        raise NotImplementedError("Drive is not implemented yet")
