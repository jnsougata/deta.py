from .errors import *
from .route import Route
from .utils import Field, Update, Query
from typing import List, Dict, Any, Optional


__all__ = ['_Base']


class _Base:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__route = Route(deta)

    def __str__(self):
        return self.name

    async def add_field(self, key: str, field: Field, force: bool = False) -> Dict[str, Any]:
        """
        adds a field to an existing key.
        if field already exists, old value will be overwritten.
        """
        if not force:
            return await self.update(key=key, updates=[Update.set([field])])
        try:
            return await self.update(key=key, updates=[Update.set([field])])
        except NotFound:
            return await self.put(key=key, field=field)

    async def remove_field(self, key: str, field_name: str) -> Dict[str, Any]:
        """
        removes a field from an existing key.
        """
        return await self.update(key=key, updates=[Update.remove([Field(field_name, None)])])

    async def fetch(self, key: str) -> Dict[str, Any]:
        """
        fetches a single item from deta by key.
        """
        return await self.__route._fetch(base_name=self.name, key=key)

    async def fetch_all(self) -> List[Dict[str, Any]]:
        """
        fetches all key and values from given base.
        """
        container = []

        async def recurse(last: Optional[str]):
            data = await self.__route._fetch_all(base_name=self.name, last=last)
            last_from_response = data['paging'].get('last')
            if last_from_response:
                container.extend(data['items'])
                await recurse(last_from_response)
            else:
                container.extend(data['items'])
                return container

        return await recurse(None)

    async def put(self, key: str, field: Field) -> Dict[str, Any]:
        """
        adds a field to base with given key.
        if key already exists, old value will be overwritten.
        """
        payload = {"items": [{"key": str(key), field.name: field.value}]}
        return await self.__route._put(base_name=self.name, json_data=payload)

    async def put_many(self, key: str, fields: List[Field]) -> Dict[str, Any]:
        """
        adds multiple field to base with given single key.
        if key already exists, old value will be overwritten.
        """
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        payload = {"items": [data]}
        return await self.__route._put(base_name=self.name, json_data=payload)

    async def put_bulk(self, keys: List[str], bulk_fields: List[List[Field]]) -> Dict[str, Any]:
        """
        adds multiple fields to base with given keys.
        if any key already exists, old value will be overwritten.
        """
        if len(keys) != len(bulk_fields):
            raise ValueError("keys and bulk_fields must be the same in length")
        form = []
        for key, fields in zip(keys, bulk_fields):
            data = {field.name: field.value for field in fields}
            data['key'] = str(key)
            form.append(data)
        payload = {"items": form}
        return await self.__route._put(base_name=self.name, json_data=payload)

    async def delete(self, key: str) -> Dict[str, Any]:
        """
        removes a single key, and it's value from base.
        """
        return await self.__route._delete(base_name=self.name, key=key)

    async def delete_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        removes multiple keys and their values from base with given keys.
        """
        return await self.__route._delete_many(base_name=self.name, keys=keys)

    async def insert(self, key: str, field: Field) -> Dict[str, Any]:
        """
        creates a field to base with given key if any field with same key doesn't exist.
        """
        payload = {"item": {"key": str(key), field.name: field.value}}
        return await self.__route._insert(base_name=self.name, json_data=payload)

    async def insert_many(self, key: str, fields: List[Field]) -> Dict[str, Any]:
        """
        creates multiple fields to base with given key if any of fields with same key doesn't exist.
        Uses a single call to API.
        """
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        payload = {"item": data}
        return await self.__route._insert(base_name=self.name, json_data=payload)

    async def update(self, key: str, updates: List[Update]) -> Dict[str, Any]:
        """
        updates a field only if a field with given key exists.
        """
        payload = {}
        for update in updates:
            payload.update(update._value)
        return await self.__route._update(base_name=self.name, key=key, update_payload=payload)

    async def query(
            self,
            query: Query,
            *,
            limit: Optional[int] = None,
            last: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        queries base with given query.
        """
        return await self.__route._query(base_name=self.name, query_data=query._data, limit=limit, last=last)
