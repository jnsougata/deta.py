import io
from aiohttp import ClientSession
from .route import _Route, PathLike
from typing import List, Dict, Optional, Union, Any


class _Drive:

    def __init__(self, name: str, project_key: str, session: ClientSession):
        self.name = name
        self._route = _Route(project_key, session)

    async def close(self):
        await self.session.close()

    async def files(self, limit: Optional[int] = None, prefix: Optional[str] = None) -> Optional[List[str]]:
        
        def get_last(response: dict):
            if response.get('paging') and response.get('paging').get('last'):
                return response['paging']['last']
            return None

        names = []
        if not limit and not prefix:
            ini_resp = await self._route.files(drive=self.name)
            names.extend(ini_resp['names'])
            last = get_last(ini_resp)
            while last:
                resp = await self._route.files(drive=self.name, last=last)
                names.extend(resp['names'])
                last = get_last(resp)
        elif not limit and prefix:
            ini_resp = await self._route.files(drive=self.name, prefix=prefix)
            names.extend(ini_resp['names'])
            last = get_last(ini_resp)
            while last:
                resp = await self._route.files(drive=self.name, last=last, prefix=prefix)
                names.extend(resp['names'])
                last = get_last(resp)
        else:
            resp = await self._route.files(drive=self.name, limit=limit, prefix=prefix)
            names.extend(resp['names'])

        return names

    async def delete(self, *names: str) -> Dict[str, Any]:
        return await self._route.delete_files(drive=self.name, keys=list(names))

    async def upload(self, content: PathLike, name: str) -> Dict[str, Any]:
        return await self._route.upload_file(drive=self.name, name=name, content=content)

    async def get(self, name: str) -> io.BytesIO:
        stream = await self._route.get_file(drive=self.name, name=name)
        buffer = b""
        async for data, end_of_http_chunk in stream.content.iter_chunks():
            buffer += data
            if end_of_http_chunk:
                buffer = b""
        return io.BytesIO(buffer)
