import aiohttp
from .base import _Base


class Deta:

    def __init__(self, *, project_key: str, session: aiohttp.ClientSession):
        self._session = session
        self._project_key = project_key

    def base(self, name: str) -> _Base:
        return _Base(name=name, deta=self)
