import asyncio
import aiohttp
from .base import _Base


class Deta:

    def __init__(self, *, token: str):
        self.token = token
        self.session = None

    async def connect(self, *, session: aiohttp.ClientSession = None, loop: asyncio.AbstractEventLoop = None):
        """
        creates a new session for Deta to make requests to the API
        """
        if session is None:
            if loop:
                self.session = aiohttp.ClientSession(loop=loop)
            else:
                self.session = aiohttp.ClientSession()
        else:
            self.session = session

    async def close(self):
        """
        closes the existing session
        """
        await self.session.close()

    def base(self, name: str) -> _Base:
        """
        creates a new instance of the Base
        """
        return _Base(name=name, deta=self)

    def drive(self):
        raise NotImplementedError("Drive is not implemented yet")
