import asyncio
import os

import aiohttp
from .base import Base
from .drive import Drive
from typing import Optional


class Deta:
    """
    Base class for Deta

    Parameters
    ----------
    project_key : str
        Project key to be used for requests
    session : aiohttp.ClientSession | None
        External client session to be used for requests
    loop : asyncio.AbstractEventLoop | None
        Event loop to be used for requests
    """

    def __init__(
        self,
        project_key: str,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        if not project_key:
            raise ValueError('project key is required')
        self.token = project_key
        assert self.token, 'project key is required'
        assert len(self.token.split('_')) == 2, 'invalid project key'
        if not session:
            self.session = aiohttp.ClientSession(loop=loop)
        else:
            self.session = session
        self.session.headers.update({'X-API-Key': self.token, 'Content-Type': 'application/json'})
        self.project_id = self.token.split('_')[0]

    @classmethod
    def from_env(
        cls,
        session: Optional[aiohttp.ClientSession] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> 'Deta':

        return cls(os.environ.get("DETA_PROJECT_KEY"), session=session, loop=loop)

    async def __aenter__(self):
        return self

    async def __aexit__(self, _, exc, __):
        await self.session.close()
        if exc:
            raise exc

    async def close(self):
        """
        Close the client session
        """
        await self.session.close()

    def base(self, name: str) -> Base:
        """
        Creates a lazy instance of Base

        Parameters
        ----------
        name : str
            Name of the base

        Returns
        -------
        Base
            Instance of Base
        """
        return Base(name, self.project_id, self.session)

    def drive(self, name: str) -> Drive:
        """
        Create a lazy instance of Drive

        Parameters
        ----------
        name : str
            Name of the drive

        Returns
        -------
        Drive
            Instance of Drive
        """
        return Drive(name, self.project_id, self.session)
