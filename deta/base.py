import asyncio
from aiohttp import ClientSession
from typing import List, Optional
from .utils import Record, Updater, Query, Result


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
    
    async def put(self, *records: Record) -> Result:
        if not records:
            raise ValueError('at least one record must be provided')
        if len(records) > 25:
            raise ValueError('cannot put more than 25 records at a time')
        payload = {"items": [record.json() for record in records]}
        resp = await self.session.put(
            f'{self.root}/items', 
            json=payload, 
            headers=self._auth_headers
        )
        return Result(resp, 207)
    
    async def delete(self, *keys: str) -> List[Result]:
        if not keys:
            raise ValueError('at least one key must be provided')
        if len(keys) == 1:
            resp = await self.session.delete(f'{self.root}/items/{str(keys[0])}', headers=self._auth_headers)
            return [Result(resp)]
        responses = await asyncio.gather(*[self.session.delete(f'{self.root}/items/{str(k)}') for k in keys])
        return [Result(r) for r in responses]

    async def get(self, *keys: str) -> List[Result]:
        if not keys:
            raise ValueError('at least one key must be provided')
        if len(keys) == 1:
            resp = await self.session.get(f'{self.root}/items/{str(keys[0])}', headers=self._auth_headers)
            return [Result(resp)]

        tasks = [self.session.get(f'{self.root}/items/{str(k)}', headers=self._auth_headers) for k in keys]
        responses = await asyncio.gather(*tasks)
        return [Result(r) for r in responses]
    
    async def update(self, key: str, updater: Updater) -> Result:
        resp = await self.session.patch(
            f'{self.root}/items/{key}',
            headers=self._auth_headers,
            json=updater.json()
        )
        return Result(resp)

    async def insert(self, *records: Record) -> List[Result]:
        if not records:
            raise ValueError('at least one record must be provided')
        tasks = [self.session.post(
            f'{self.root}/items', headers=self._auth_headers, json=p
        ) for p in [{"item": r.json()} for r in records]]
        responses = await asyncio.gather(*tasks)
        return [Result(r, 201) for r in responses]

    async def fetch(
            self,
            queries: List[Query],
            *,
            limit: Optional[int] = None,
            last: Optional[str] = None
    ) -> Result:
        payload = {"query": [q.json() for q in queries]}
        if limit:
            payload['limit'] = limit
        if last:
            payload['last'] = last
        resp = await self.session.post(f'{self.root}/query', headers=self._auth_headers, json=payload)
        return Result(resp)

    async def fetch_until_end(self, queries: List[Query]) -> List[Result]:
        results = []
        result = await self.fetch(queries)
        results.append(result)
        data = await result.json()
        try:
            last = data['paging']['last']
        except KeyError:
            return results
        while last:
            result = await self.fetch(queries, last=last)
            results.append(result)
            data = await result.json()
            try:
                last = data['paging']['last']
            except KeyError:
                return results
