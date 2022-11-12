import io
import sys
import asyncio
import aiohttp
from .errors import *
from urllib.parse import quote_plus
from typing import Optional, Union, List, Dict, Any



PathLike = Union[str, bytes]


class _Route:

    MIME_TYPE = 'application/json'
    CONTENT_TYPE = 'application/octet-stream'
    BASE = 'https://database.deta.sh/v1'
    DRIVE = 'https://drive.deta.sh/v1'
    MAX_UPLOAD_SIZE = 10485760  # 10MB

    def __init__(self, project_key: str, session: aiohttp.ClientSession):
        self.session = session
        self.pid = project_key.split('_')[0]
        self.base_url = f'{self.BASE}/{self.pid}/'
        self.drive_url = f'{self.DRIVE}/{self.pid}/'
        self.base_headers = {'X-API-Key': project_key, 'Content-Type': self.MIME_TYPE}
        self.drive_headers = {'X-API-Key': project_key, 'Content-Type': self.CONTENT_TYPE}

    @staticmethod
    def fmt_error(emap: dict) -> str:
        return '\n'.join(emap['errors'])

    async def close(self):
        await self.session.close()

    async def get(self, name: str, key: str):
        ep = self.base_url + name + '/items/' + key
        resp = await self.session.get(ep, headers=self.base_headers)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            return None

    async def fetch_all(self, name: str):
        ep = self.base_url + name + '/query'
        items = []
        ini_data = await (await self.session.post(ep, headers=self.base_headers)).json()
        last = ini_data['paging'].get('last')
        items.extend(ini_data['items'])
        while last:
            data = await (await self.session.post(ep, headers=self.base_headers, data={'last': last})).json()
            items.extend(data['items'])
            last = data['paging'].get('last')
        return items

    async def put(self, name: str, payload: dict):
        ep = self.base_url + name + '/items'
        resp = await self.session.put(ep, headers=self.base_headers, json=payload)
        if resp.status == 207:
            data = await resp.json()
            if 'failed' in data:
                print('Warning: some items failed because of internal processing error', file=sys.stderr)
        if resp.status == 400:
            e = await resp.json()
            raise BadRequest(e['errors'][0])
        return await resp.json()

    async def delete(self, name: str, key: str):
        ep = self.base_url + name + '/items/' + key
        await self.session.delete(ep, headers=self.base_headers)
        return key

    async def delete_many(self, name: str, keys: List[str]):
        task = [asyncio.create_task(self.delete(name, key)) for key in keys]
        return await asyncio.gather(*task)

    async def insert(self, name: str, payload: dict):
        ep = self.base_url + name + '/items'
        resp = await self.session.post(ep, headers=self.base_headers, json=payload)
        if resp.status == 201:
            return await resp.json()
        if resp.status == 409:
            raise KeyConflict('key already exists in Deta base')
        if resp.status == 400:
            raise BadRequest('invalid insert payload')

    async def update(self, name: str, key: str, payload: dict):
        ep = self.base_url + name + '/items/' + key
        resp = await self.session.patch(ep, headers=self.base_headers, json=payload)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            raise NotFound('key does not exist in Deta Base')
        if resp.status == 400:
            raise BadRequest('invalid update payload')

    async def fetch(self, name: str, limit: Optional[int], last: Optional[str], queries: List[Dict[str, Any]]):
        ep = self.base_url + name + '/query'
        if limit and limit > 1000:
            raise ValueError('limit must be less or equal to 1000')
        if limit and limit <= 0:
            raise ValueError('limit must be greater than 0')
        payload = {'query': queries}
        items = []
        if last and not limit:
            payload['last'] = last
            ini_data = await (await self.session.post(ep, headers=self.base_headers, json=payload)).json()
            items.extend(ini_data['items'])
            last = ini_data['paging'].get('last')
            while last:
                data = await (await self.session.post(ep, headers=self.base_headers, json={'last': last})).json()
                items.extend(data['items'])
                last = data['paging'].get('last')
        elif not last and limit:
            payload['limit'] = limit
            resp = await self.session.post(ep, headers=self.base_headers, json=query)
            items.extend((await resp.json())['items'])
        elif last and limit:
            payload['last'] = last
            payload['limit'] = limit
            resp = await (await self.session.post(ep, headers=self.base_headers, json=query)).json()
            items.extend(resp['items'])
        else:
            ini_data = await (await self.session.post(ep, headers=self.base_headers, json=payload)).json()
            items.extend(ini_data['items'])
            last = ini_data['paging'].get('last')
            while last:
                payload['last'] = last
                resp = await (await self.session.post(ep, headers=self.base_headers, json=payload)).json()
                items.extend(resp['items'])
                last = resp['paging'].get('last')
        return items

    async def files(
            self,
            drive: str,
            limit: Optional[int] = None,
            prefix: str = None,
            last: str = None,
    ):
        tail = f'/files?'
        if limit and limit > 1000:
            raise ValueError('limit must be less or equal to 1000')
        if limit and limit <= 0:
            raise ValueError('limit must be greater than 0')
        if limit:
            tail += f'limit={limit}'
        if prefix:
            tail += f'&prefix={prefix}'
        if last:
            tail += f'&last={last}'
        ep = self.drive_url + drive + tail
        resp = await self.session.get(ep, headers=self.base_headers)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 400:
            error_map = await resp.json()
            raise BadRequest('\n'.join(error_map['errors']))

    async def delete_files(self, drive: str, keys: List[str]):
        ep = self.drive_url + drive + '/files'
        json_data = {'names': keys}
        resp = await self.session.delete(ep, headers=self.base_headers, json=json_data)
        return await resp.json()

    async def upload_file(self, *, drive: str, name: str, content: PathLike) -> dict:
        if isinstance(content, str):
            file = open(content, 'rb')
        elif isinstance(content, bytes):
            file = io.BytesIO(content)
        else:
            raise ValueError('path must be a string or bytes')
        final, status = {}, 0
        chunks = file.read()

        if not len(chunks) > self.MAX_UPLOAD_SIZE:
            ep = f'{self.drive_url}{drive}/files?name={quote_plus(name)}'
            resp = await self.session.post(ep, headers=self.drive_headers, data=chunks)
            file.close()
            final, status = await resp.json(), resp.status
        else:
            ep = f'{self.drive_url}{drive}/files?name={quote_plus(name)}'
            ini = await self.session.post(ep, headers=self.drive_headers)
            if ini.status == 202:
                upload_id = (await ini.json())['upload_id']
                chunked = [
                    chunks[i:i+self.MAX_UPLOAD_SIZE]
                    for i in range(0, len(chunks), self.MAX_UPLOAD_SIZE)
                ]
                upload_tasks = []
                for i, chunk in enumerate(chunked[:-1]):
                    post_ep = (
                        f"{self.drive_url}{drive}/uploads/{upload_id}/parts?name={name}&part={i + 1}"
                    )
                    upload_tasks.append(
                        asyncio.create_task(self.session.post(post_ep, headers=self.drive_headers, data=chunk))
                    )
                gathered = await asyncio.gather(*upload_tasks)
                ok = True
                for item in gathered:
                    if isinstance(item, Exception):
                        success = False
                        abort_ep = f"{self.drive_url}{drive}/uploads/{upload_id}?name={name}"
                        await self.session.delete(abort_ep, headers=self.drive_headers)
                        file.close()
                        raise Exception("failed to upload a chunked part")
                if ok:
                    last_chunk_ep = f"{self.drive_url}{drive}/uploads/{upload_id}?name={name}"
                    resp = await self.session.patch(last_chunk_ep, headers=self.drive_headers, data=chunked[-1])
                    file.close()
                    final, status = await resp.json(), resp.status

        if status == 200 or status == 201:
            return final
        elif status == 400:
            raise BadRequest(self.fmt_error(final))
        else:
            raise Exception(self.fmt_error(final))

    async def get_file(self, *, drive: str, name: str) -> aiohttp.ClientResponse:
        ep = self.drive_url + drive + f'/files/download?name={quote_plus(name)}'
        resp = await self.session.get(ep, headers=self.drive_headers)
        if resp.status == 200:
            return resp
        if resp.status == 400:
            raise BadRequest(self.fmt_error(await resp.json()))
        if resp.status == 404:
            raise NotFound(self.fmt_error(await resp.json()))
