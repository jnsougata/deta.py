import sys
import aiohttp


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
        data = await resp.json()
        if len(data) == 1:
            return None
        return data

    async def _fetch_all(self, session: aiohttp.ClientSession, name: str):
        ep = self.__root + name + '/query'
        resp = await session.post(ep, headers=self.__headers)
        return await resp.json()


    async def _put(self, session: aiohttp.ClientSession, name: str, json_data: dict):
        ep = self.__root + name + '/items'
        resp = await session.put(ep, headers=self.__headers, json=json_data)
        return await resp.json()

    async def _delete(self, session: aiohttp.ClientSession, name: str, key: str):
        ep = self.__root + name + '/items/' + key
        resp = await session.delete(ep, headers=self.__headers)
        return None

    async def _delete_many(self, session: aiohttp.ClientSession, name: str, keys: list):
        for key in keys:
            await self._delete(session, name, key)
        return None

    async def _insert(self, session: aiohttp.ClientSession, name: str, json_data: dict):
        ep = self.__root + name + '/items'
        resp = await session.post(ep, headers=self.__headers, json=json_data)
        return resp.status, await resp.json()

    async def _update(self, session: aiohttp.ClientSession, name: str, key: str, json_data: dict):
        ep = self.__root + name + '/items/' + key
        resp = await session.patch(ep, headers=self.__headers, json=json_data)
        return await resp.json()

    async def _query(self, session: aiohttp.ClientSession, json_data: dict):
        ep = self.__root + name + '/query'
        resp = await session.get(ep, headers=self.__headers, json=json_data)
        return await resp.json()
