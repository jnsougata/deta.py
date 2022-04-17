from .route import Route
from typing import List, Dict, Any, Union
from .utils import Field, Update, dict_to_field



__all__ = ['_Base']


class _Base:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__session = deta._session
        self.__route = Route(deta._project_key)

    def __str__(self):
        return self.name

    async def append_field(self, key: str, field: Field):
        old_data = await self.fetch(key)
        if old_data is None:
            raise ValueError("key does not exist")
        fields = dict_to_field(old_data)
        fields.append(field)
        return await self.put_many(key=key, fields=fields)

    async def remove_field(self, key: str, field_name: str):
        old_data = await self.fetch(key)
        if old_data is None:
            raise ValueError("key does not exist")
        try:
            old_data.pop(field_name)
            fields = dict_to_field(old_data)
            return await self.put_many(key=key, fields=fields)
        except KeyError:
            return {field_name: None}


    async def fetch(self, key: str) -> Dict[str, Any]:
        return await self.__route._fetch(self.__session, name=self.name, key=key)

    async def fetch_all(self) -> List[Dict[str, Any]]:
        return await self.__route._fetch_all(self.__session, name=self.name)

    async def put(self, *, key: str, field: Field) -> Dict[str, Any]:
        payload = {"items": [{"key": str(key), field.name: field.value}]}
        return await self.__route._put(self.__session, name=self.name, json_data=payload)

    async def put_many(self, *, key: str, fields: List[Field]) -> Dict[str, Any]:
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        payload = {"items": [data]}
        return await self.__route._put(self.__session, name=self.name, json_data=payload)

    async def put_bulk(self, *, keys: List[str], bulk_fields: List[List[Field]]) -> List[Dict[str, Any]]:
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
        status, data = await self.__route._insert(self.__session, name=self.name, json_data=payload)
        if status == 201:
            return data
        if status == 409:
            raise KeyConflict('key already exists in Deta base')
        if status == 400:
            raise BadRequest('invalid insert payload')

    async def insert_many(self, *, key: str, fields: List[Field]):
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        payload = {"item": data}
        return await self.__route._insert(self.__session, name=self.name, json_data=payload)


    async def update(self, *, key: str, updates: List[Update]):
        payload = {}
        for update in updates:
            payload.update(update._value)
        return await self.__route._update(self.__session, name=self.name, key=key, json_data=payload)
