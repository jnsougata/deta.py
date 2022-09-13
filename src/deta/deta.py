import os
import asyncio
import aiohttp
from .base import _Base
from .drive import _Drive
from typing import Optional


class Deta:

    def __init__(self, project_key: Optional[str] = None):
        self.session = None
        self.token = project_key or os.getenv('DETA_ACCESS_TOKEN')
        assert self.token, 'project key is required'

    async def connect(
            self,
            *,
            session: Optional[aiohttp.ClientSession] = None,
            loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        if not session:
            self.session = aiohttp.ClientSession(loop=loop)
        else:
            self.session = session

    async def close(self):
        await self.session.close()

    def base(self, name: str) -> _Base:
        return _Base(name=name, deta=self)

    def drive(self, name: str) -> _Drive:
        return _Drive(name=name, deta=self)
