from .route import Route
from .utils import Field, Updater
from typing import List, Dict, Any, Union


__all__ = ['_Base']


class _Base:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.cached = None
        self.__session = deta._session
        self.__route = Route(deta._project_key)

    def __str__(self):
        return self.name

    async def cache(self):
        self.cached = await self.fetch_all()
        return self.cached

    def get(self, key: str):
        if self.cached:
            for item in self.cached['items']:
                if item['key'] == key:
                    return item
        return None

    async def fetch(self, key: str):
        return await self.__route._fetch(self.__session, name=self.name, key=key)

    async def fetch_all(self):
        return await self.__route._fetch_all(self.__session, name=self.name)

    async def put(self, *, key: str, field: Field):
        payload = {"items": [{"key": str(key), field.name: field.value}]}
        return await self.__route._put(self.__session, name=self.name, json_data=payload)

    async def put_many(self, *, key: str, fields: List[Field]):
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        payload = {"items": [data]}
        return await self.__route._put(self.__session, name=self.name, json_data=payload)

    async def put_bulk(self, *, keys: List[str], bulk_fields: List[List[Field]]):
        if len(keys) != len(bulk_fields):
            raise ValueError("keys and bulk_fields must be the same in length")
        form = []
        for key, fields in zip(keys, bulk_fields):
            data = {field.name: field.value for field in fields}
            data['key'] = str(key)
            form.append(data)
        payload = {"items": form}
        return await self.__route._put(self.__session, name=self.name, json_data=payload)

    async def delete(self, key: str):
        return await self.__route._delete(self.__session, name=self.name, key=key)

    async def delete_many(self, keys: List[str]):
        return await self.__route._delete_many(self.__session, name=self.name, keys=keys)

    async def insert(self, *, key: str, field: Field):
        payload = {"item": {"key": str(key), field.name: field.value}}
        return await self.__route._insert(self.__session, name=self.name, json_data=payload)

    async def insert_many(self, *, key: str, fields: List[Field]):
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        payload = {"item": data}
        return await self.__route._insert(self.__session, name=self.name, json_data=payload)

    async def update(self, *, key: str, data: List[Dict[str, Any]]):
        payload = {}
        for item in data:
            payload.update(item)
        print(payload)
        return await self.__route._update(self.__session, name=self.name, key=key, json_data=payload)
