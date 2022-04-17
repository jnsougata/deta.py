import sys
import aiohttp
from .errors import *


class Route:

    __MIME = 'application/json'
    __BASE = 'https://database.deta.sh/v1/'

    def __init__(self, token):
        self.__project_id = token.split('_')[0]
        self.__root = self.__BASE + self.__project_id + '/'
        self.__headers = {'Content-Type': self.__MIME, 'X-API-Key': token}

    async def _fetch(self, session: aiohttp.ClientSession, *, name: str, key: str):
        ep = self.__root + name + '/items/' + key
        resp = await session.get(ep, headers=self.__headers)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            return None

    async def _fetch_all(self, session: aiohttp.ClientSession, name: str):
        ep = self.__root + name + '/query'
        resp = await session.post(ep, headers=self.__headers)
        if resp.status == 200:
            data = await resp.json()
            return data['items']
        return None


    async def _put(self, session: aiohttp.ClientSession, name: str, json_data: dict):
        ep = self.__root + name + '/items'
        resp = await session.put(ep, headers=self.__headers, json=json_data)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 207:
            print('Warning: items failed because of internal processing error', file=sys.stderr)
            return await resp.json()
        if resp.status == 400:
            e = await resp.json()
            raise BadRequest(e['errors'][0])

    async def _delete(self, session: aiohttp.ClientSession, name: str, key: str):
        ep = self.__root + name + '/items/' + key
        await session.delete(ep, headers=self.__headers)
        return key

    async def _delete_many(self, session: aiohttp.ClientSession, name: str, keys: list):
        for key in keys:
            await self._delete(session, name, key)
        return keys

    async def _insert(self, session: aiohttp.ClientSession, name: str, json_data: dict):
        ep = self.__root + name + '/items'
        resp = await session.post(ep, headers=self.__headers, json=json_data)
        if resp.status == 201:
            return await resp.json()
        if resp.status == 409:
            raise KeyConflict('key already exists in Deta base')
        if resp.status == 400:
            raise BadRequest('invalid insert payload')

    async def _update(self, session: aiohttp.ClientSession, name: str, key: str, json_data: dict):
        ep = self.__root + name + '/items/' + key
        resp = await session.patch(ep, headers=self.__headers, json=json_data)
        if resp.status == 200:
            return await resp.json()
        if resp.status == 404:
            raise NotFound('key does not exist in Deta Base')
        if resp.status == 400:
            raise BadRequest('invalid update payload')

    async def _query(self, session: aiohttp.ClientSession, json_data: dict):
        ep = self.__root + name + '/query'
        resp = await session.get(ep, headers=self.__headers, json=json_data)
        return await resp.json()
