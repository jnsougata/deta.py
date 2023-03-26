import asyncio
from aiohttp import ClientSession
from .utils import Record, Updater, Query
from typing import List, Dict, Any, Optional


class Base:
    def __init__(self, name: str, project_key: str, session: ClientSession):
        self.name = name
        self.session = session
        self.project_id = project_key.split('_')[0]
        self.root = f'https://database.deta.sh/v1/{self.project_id}/{name}'
        self._auth_headers = {'X-API-Key': project_key, 'Content-Type': 'application/json'}

    def __str__(self):
        return self.name

    async def close(self):
        return await self.session.close()
    
    async def put(self, *records: Record) -> Dict[str, Any]:
        if len(records) > 25:
            raise ValueError('cannot put more than 25 records at a time')
        payload = {"items": [record.json() for record in records]}
        resp = await self.session.put(
            f'{self.root}/items', 
            json=payload, 
            headers=self._auth_headers
        )
        return await resp.json()
    
    async def delete(self, *keys: str) -> List[str]:
        if not keys:
            return []
        if len(keys) == 1:
            await self.session.delete(f'{self.root}/items/{str(keys[0])}', headers=self._auth_headers)
        tasks = [self.session.delete(f'{self.root}/items/{str(k)}') for k in keys]
        await asyncio.gather(*tasks)
        return list(keys)

    async def get(self, *keys: str) -> List[Dict[str, Any]]:
        if not keys:
            container = []
            r = await self.session.post(f'{self.root}/query', headers=self._auth_headers)
            data = await r.json()
            container.extend(data.get('items', []))
            try:
                last = data['paging']['last']
            except KeyError:
                return container
            while last:
                r = await self.session.post(f'{self.root}/query', headers=self._auth_headers, json={'last': last})
                data = await r.json()
                if data.get('items'):
                    container.extend(data['items'])
                try:
                    last = data['paging']['last']
                except KeyError:
                    return container

        if len(keys) == 1:
            return [
                await (await self.session.get(f'{self.root}/items/{str(keys[0])}', headers=self._auth_headers)).json()]

        tasks = [self.session.get(f'{self.root}/items/{str(k)}', headers=self._auth_headers) for k in keys]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]
    
    async def update(self, key: str, updater: Updater) -> Dict[str, Any]:
        resp = await self.session.patch(
            f'{self.root}/items/{key}',
            headers=self._auth_headers,
            json=updater.json()
        )
        return await resp.json()

    async def insert(self, *records: Record) -> Optional[List[Dict[str, Any]]]:
        if not records:
            return None
        tasks = [self.session.post(
            f'{self.root}/items', headers=self._auth_headers, json=p
        ) for p in [{"item": r.json()} for r in records]]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

    async def query(self, *queries: Query, limit: Optional[int] = None, last: Optional[str] = None) -> Dict[str, Any]:
        translated = [q.json() for q in queries]
        payload = {"query": translated}
        if limit:
            payload['limit'] = limit
        if last:
            payload['last'] = last
        resp = await self.session.post(f'{self.root}/query', headers=self._auth_headers, json=payload)
        return await resp.json()
