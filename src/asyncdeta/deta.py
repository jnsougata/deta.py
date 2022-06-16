import asyncio
import aiohttp
from .base import _Base
from .drive import _Drive


class Deta:

    def __init__(self, project_key: str):
        if project_key:
            self.token = project_key
        else:
            raise ValueError("project key is required")
        self.session = None

    async def connect(
            self,
            *,
            session: aiohttp.ClientSession = None,
            loop: asyncio.AbstractEventLoop = None
    ):
        """
        creates/assigns a session for Deta to make requests to the API
        """
        if not session:
            self.session = aiohttp.ClientSession(loop=loop)
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

    def drive(self, name: str) -> _Drive:
        return _Drive(name=name, deta=self)
