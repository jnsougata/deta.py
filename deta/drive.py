import io
import os
import secrets
import asyncio
from urllib.parse import quote_plus
from aiohttp import ClientSession, StreamReader
from typing import Dict, Optional, Any

MAX_UPLOAD_SIZE = 10485760  # 10MB


class Drive:

    def __init__(self, name: str, project_key: str, session: ClientSession):
        self.name = name
        self.session = session
        self.project_id = project_key.split('_')[0]
        self.root = f'https://drive.deta.sh/v1/{self.project_id}/{name}'
        self._auth_headers = {'X-Api-Key': project_key, 'Content-Type': 'application/octet-stream'}

    async def close(self):
        await self.session.close()
    
    async def put(
        self, 
        content: os.PathLike, 
        *,
        save_as: Optional[str] = None,
        folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        if isinstance(content, str):
            file = open(content, 'rb')
            if not save_as:
                save_as = file.name
        elif isinstance(content, bytes):
            file = io.BytesIO(content)
            if not save_as:
                save_as = secrets.token_hex(8)
        else:
            raise ValueError('path must be a string or bytes')
        
        if folder:
            save_as = f'{folder}/{save_as}'
        with file:
            content = file.read()
            if not len(content) > MAX_UPLOAD_SIZE:
                resp = await self.session.post(
                    f'{self.root}/files?name={quote_plus(save_as)}', 
                    headers=self._auth_headers, data=content
                )
                return await resp.json()

            r = await self.session.post(
                f'{self.root}/uploads?name={quote_plus(save_as)}', 
                headers=self._auth_headers
            )
            if r.status == 202:
                resp_data = await r.json()
                upload_id = resp_data['upload_id']
                name = resp_data['name']
                chunked = [
                    content[i:i+MAX_UPLOAD_SIZE] for i in range(0, len(content), MAX_UPLOAD_SIZE)
                ]
                upload_tasks = [
                    self.session.post(
                        f"{self.root}/uploads/{upload_id}/parts?name={name}&part={i + 1}", 
                        headers=self._auth_headers, 
                        data=chunk
                    )
                    for i, chunk in enumerate(chunked)
                ]
                gathered = await asyncio.gather(*upload_tasks)
                status_codes = [r.status == 200 for r in gathered]
                headers = self._auth_headers.copy()
                headers['Content-Type'] = 'application/json'
                if all(status_codes):
                    resp = await self.session.patch(f"{self.root}/uploads/{upload_id}?name={name}",headers=headers)
                    return await resp.json()
                else:
                    await self.session.delete(f"{self.root}/uploads/{upload_id}?name={name}", headers=headers)
                    raise Exception("failed to upload a chunked part")

    async def files(
        self, 
        limit: Optional[int] = None, 
        prefix: Optional[str] = None, 
        last: Optional[str] = None
    ) -> Dict[str, Any]:
        headers = self._auth_headers.copy()
        headers['Content-Type'] = 'application/json'
        if not limit and not prefix and not last:
            initial_resp = await self.session.get(f'{self.root}/files', headers=headers)
            initial_data = await initial_resp.json()
            last = None
            files = initial_data['names']
            if initial_data.get('paging', {}).get('last', None):
                last = initial_data['paging']['last']
            while last:
                data = await (await self.session.get(f'{self.root}/files?last={last}', headers=headers)).json()
                files.extend(data['names'])
                if data.get('paging', {}).get('last', None):
                    last = data['paging']['last']
            return {'names': files}

        if not limit or limit > 1000 or limit < 0:
            limit = 1000
        url = f'{self.root}/files?limit={limit}'
        if prefix:
            url += f'&prefix={prefix}'
        if last:
            url += f'&last={last}'
        resp = await self.session.get(url, headers=headers)
        return await resp.json()

    async def delete(self, *names: str) -> Dict[str, Any]:
        headers = self._auth_headers.copy()
        headers['Content-Type'] = 'application/json'
        r = await self.session.delete(f'{self.root}/files', headers=headers,json={'names': list(names)})
        return await r.json()

    async def get(self, filename: str, *, folder: str = None) -> StreamReader:
        if folder:
            filename = f'{folder}/{filename}'
        resp = await self.session.get(
            f'{self.root}/files/download?name={filename}',
            headers=self._auth_headers
        )
        return resp.content
