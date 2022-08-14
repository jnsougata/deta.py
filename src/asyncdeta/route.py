import io
import sys
import asyncio
import aiohttp
from .errors import *
from typing import Any, Optional, Union, Tuple
from urllib.parse import quote_plus


PathLike = Union[str, bytes]


class _Route:

    MIME_TYPE = 'application/json'
    CONTENT_TYPE = 'application/octet-stream'
    BASE = 'https://database.deta.sh/v1/'
    DRIVE = 'https://drive.deta.sh/v1/'
    MAX_UPLOAD_SIZE = 10485760  # 10MB

    def __init__(self, deta):
        self.cs = deta.session
        self.pid = deta.token.split('_')[0]
        self.base_url = self.BASE + self.pid + '/'
        self.drive_url = self.DRIVE + self.pid + '/'
        self.base_headers = {'X-API-Key': deta.token, 'Content-Type': self.MIME_TYPE}
        self.drive_headers = {'X-API-Key': deta.token, 'Content-Type': self.CONTENT_TYPE}

    @staticmethod
    def fmt_error(emap: dict) -> str:
        return '\n'.join(emap['errors'])

    async def _close(self):
        await self.cs.close()

    async def _fetch(self, base_name: str, key: str):
        ep = self.base_url + base_name + '/items/' + key
        resp = await self.cs.get(ep, headers=self.base_headers)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            return None

    async def _fetch_all(self, base_name: str):
        ep = self.base_url + base_name + '/query'
        items = []
        ini_data = await (await self.cs.post(ep, headers=self.base_headers)).json()
        last = ini_data['paging'].get('last')
        items.extend(ini_data['items'])
        while last:
            data = await (await self.cs.post(ep, headers=self.base_headers, data={'last': last})).json()
            items.extend(data['items'])
            last = data['paging'].get('last')
        return items

    async def _put(self, base_name: str, json_data: dict):
        ep = self.base_url + base_name + '/items'
        resp = await self.cs.put(ep, headers=self.base_headers, json=json_data)
        if resp.status == 207:
            data = await resp.json()
            if 'failed' in data:
                print('Warning: some items failed because of internal processing error', file=sys.stderr)
        if resp.status == 400:
            e = await resp.json()
            raise BadRequest(e['errors'][0])
        return await resp.json()

    async def _delete(self, base_name: str, key: str):
        ep = self.base_url + base_name + '/items/' + key
        await self.cs.delete(ep, headers=self.base_headers)
        return key

    async def _delete_many(self, base_name: str, keys: list):
        task = [asyncio.create_task(self._delete(base_name, key)) for key in keys]
        return await asyncio.gather(*task)

    async def _insert(self, base_name: str, json_data: dict):
        ep = self.base_url + base_name + '/items'
        resp = await self.cs.post(ep, headers=self.base_headers, json=json_data)
        if resp.status == 201:
            return await resp.json()
        if resp.status == 409:
            raise KeyConflict('key already exists in Deta base')
        if resp.status == 400:
            raise BadRequest('invalid insert payload')

    async def _update(self, base_name: str, key: str, payload: dict):
        ep = self.base_url + base_name + '/items/' + key
        resp = await self.cs.patch(ep, headers=self.base_headers, json=payload)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            raise NotFound('key does not exist in Deta Base')
        if resp.status == 400:
            raise BadRequest('invalid update payload')

    async def _query(self, base_name: str, limit: Optional[int], last: Optional[str], query: dict):
        ep = self.base_url + base_name + '/query'
        if limit and limit > 1000:
            raise ValueError('limit must be less or equal to 1000')
        if limit and limit <= 0:
            raise ValueError('limit must be greater than 0')
        queries = []
        if isinstance(query, list):
            queries.extend(query)
        else:
            queries.append(query)
        payload = {'query': queries}
        items = []
        if last and not limit:
            payload['last'] = last
            ini_data = await (await self.cs.post(ep, headers=self.base_headers, json=payload)).json()
            items.extend(ini_data['items'])
            last = ini_data['paging'].get('last')
            while last:
                data = await (await self.cs.post(ep, headers=self.base_headers, json={'last': last})).json()
                items.extend(data['items'])
                last = data['paging'].get('last')
        elif not last and limit:
            payload['limit'] = limit
            resp = await self.cs.post(ep, headers=self.base_headers, json=query)
            items.extend((await resp.json())['items'])
        elif last and limit:
            payload['last'] = last
            payload['limit'] = limit
            resp = await (await self.cs.post(ep, headers=self.base_headers, json=query)).json()
            items.extend(resp['items'])
        else:
            ini_data = await (await self.cs.post(ep, headers=self.base_headers, json=payload)).json()
            items.extend(ini_data['items'])
            last = ini_data['paging'].get('last')
            while last:
                payload['last'] = last
                resp = await (await self.cs.post(ep, headers=self.base_headers, json=payload)).json()
                items.extend(resp['items'])
                last = resp['paging'].get('last')
        return items

    async def _fetch_file_list(
            self,
            drive_name: str,
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
        ep = self.drive_url + drive_name + tail
        resp = await self.cs.get(ep, headers=self.base_headers)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 400:
            error_map = await resp.json()
            raise BadRequest('\n'.join(error_map['errors']))

    async def _bulk_delete_files(self, drive_name: str, keys: list):
        ep = self.drive_url + drive_name + '/files'
        json_data = {'names': keys}
        resp = await self.cs.delete(ep, headers=self.base_headers, json=json_data)
        return await resp.json()

    async def _put_file(self, drive_name: str, remote_path: str, path: PathLike) -> dict:
        if isinstance(path, str):
            file = open(path, 'rb')
        elif isinstance(path, bytes):
            file = io.BytesIO(path)
        else:
            raise ValueError('path must be a string or bytes')
        final, status = {}, 0
        chunks = file.read()

        if not len(chunks) > self.MAX_UPLOAD_SIZE:
            ep = self.drive_url + drive_name + '/files?name=' + quote_plus(remote_path)
            resp = await self.cs.post(ep, headers=self.drive_headers, data=chunks)
            file.close()
            final, status = await resp.json(), resp.status
        else:
            ep = self.drive_url + drive_name + '/uploads?name=' + quote_plus(remote_path)
            ini = await self.cs.post(ep, headers=self.drive_headers)
            if ini.status == 202:
                upload_id = (await ini.json())['upload_id']
                chunked = [
                    chunks[i:i+self.MAX_UPLOAD_SIZE]
                    for i in range(0, len(chunks), self.MAX_UPLOAD_SIZE)
                ]
                upload_tasks = []
                for i, chunk in enumerate(chunked[:-1]):
                    post_ep = (
                        f"{self.drive_url}{drive_name}/uploads/{upload_id}/parts?name={remote_path}&part={i + 1}"
                    )
                    upload_tasks.append(
                        asyncio.create_task(self.cs.post(post_ep, headers=self.drive_headers, data=chunk))
                    )
                gathered = await asyncio.gather(*upload_tasks)
                ok = True
                for item in gathered:
                    if isinstance(item, Exception):
                        success = False
                        abort_ep = f"{self.drive_url}{drive_name}/uploads/{upload_id}?name={remote_path}"
                        await self.cs.delete(abort_ep, headers=self.drive_headers)
                        file.close()
                        raise Exception("failed to upload a chunked part")
                if ok:
                    last_chunk_ep = f"{self.drive_url}{drive_name}/uploads/{upload_id}?name={remote_path}"
                    resp = await self.cs.patch(last_chunk_ep, headers=self.drive_headers, data=chunked[-1])
                    file.close()
                    final, status = await resp.json(), resp.status

        if status == 200 or status == 201:
            return final
        elif status == 400:
            raise BadRequest(self.fmt_error(final))
        else:
            raise Exception(self.fmt_error(final))

    async def _get_file(self, drive_name, remote_path) -> bytes:
        ep = self.drive_url + drive_name + f'/files/download?name={quote_plus(remote_path)}'
        resp = await self.cs.get(ep, headers=self.drive_headers)
        if resp.status == 200:
            return resp
        if resp.status == 400:
            raise BadRequest(self.fmt_error(await resp.json()))
        if resp.status == 404:
            raise NotFound(self.fmt_error(await resp.json()))