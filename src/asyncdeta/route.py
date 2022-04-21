import sys
import aiohttp
from .errors import *


class Route:

    __MIME = 'application/json'
    __BASE = 'https://database.deta.sh/v1/'

    def __init__(self, token: str, session: aiohttp.ClientSession):
        self.__session = session
        self.__project_id = token.split('_')[0]
        self.__root = self.__BASE + self.__project_id + '/'
        self.__headers = {'Content-Type': self.__MIME, 'X-API-Key': token}

    async def _fetch(self, name: str, key: str):
        ep = self.__root + name + '/items/' + key
        resp = await self.__session.get(ep, headers=self.__headers)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            return None

    async def _fetch_all(self, name: str):
        ep = self.__root + name + '/query'
        resp = await self.__session.post(ep, headers=self.__headers)
        if resp.status == 200:
            data = await resp.json()
            return data['items']
        return None

    async def _put(self, name: str, json_data: dict):
        ep = self.__root + name + '/items'
        resp = await self.__session.put(ep, headers=self.__headers, json=json_data)
        if resp.status == 207:
            data = await resp.json()
            if 'failed' in data:
                print('Warning: some items failed because of internal processing error', file=sys.stderr)
        if resp.status == 400:
            e = await resp.json()
            raise BadRequest(e['errors'][0])
        return await resp.json()

    async def _delete(self, name: str, key: str):
        ep = self.__root + name + '/items/' + key
        await self.__session.delete(ep, headers=self.__headers)
        return key

    async def _delete_many(self, name: str, keys: list):
        for key in keys:
            await self._delete(name, key)
        return keys

    async def _insert(self, name: str, json_data: dict):
        ep = self.__root + name + '/items'
        resp = await self.__session.post(ep, headers=self.__headers, json=json_data)
        if resp.status == 201:
            return await resp.json()
        if resp.status == 409:
            raise KeyConflict('key already exists in Deta base')
        if resp.status == 400:
            raise BadRequest('invalid insert payload')

    async def _update(self, name: str, key: str, json_data: dict):
        ep = self.__root + name + '/items/' + key
        resp = await self.__session.patch(ep, headers=self.__headers, json=json_data)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            raise NotFound('key does not exist in Deta Base')
        if resp.status == 400:
            raise BadRequest('invalid update payload')

    # TODO: query is not implemented yet

    # Drive API methods

    async def _fetch_file_list(
            self,
            name: str,
            limit: int,
            prefix: str = None,
            last: str = None,
    ):
        if limit > 1000:
            raise ValueError('limit must be less or equal to 1000')
        if limit <= 0:
            raise ValueError('limit must be greater than 0')

        limit_ = limit or 1000

        tail = f'/files?limit={limit_}'
        if prefix:
            tail += f'&prefix={prefix}'
        if last:
            tail += f'&last={last}'
        ep = self.__root + name + tail

        resp = await self.__session.get(ep, headers=self.__headers)

        if resp.status == 200:
            return await resp.json()
        if resp.status == 400:
            error_map = await resp.json()
            raise BadRequest('\n'.join(error_map['errors']))

    async def _bulk_delete_files(self, name: str, keys: list):
        ep = self.__root + name + '/files'
        json_data = {'names': keys}
        resp = await self.__session.delete(ep, headers=self.__headers, json=json_data)
        return await resp.json()


