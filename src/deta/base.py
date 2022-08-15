import asyncio
from .errors import *
from typing import Union
from .route import _Route
from datetime import datetime, timedelta
from .utils import Field, Update, Query
from typing import List, Dict, Any, Optional


__all__ = ['_Base']


class _Base:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__route = _Route(deta)
        self.__expiry_key = '__expires'

    def __str__(self):
        return self.name

    async def close(self):
        """
        closes the connection to deta.
        """
        return await self.__route._close()

    @staticmethod
    def __time_to_expiry(time_value: Union[int, float, datetime]) -> Union[int, float]:
        if isinstance(time_value, datetime):
            return time_value.replace(microsecond=0).timestamp()
        else:
            return (datetime.now() + timedelta(seconds=time_value)).replace(microsecond=0).timestamp()

    async def add_field(self, key: str, field: Field, force: bool = False) -> Dict[str, Any]:
        """
        adds a field to an existing key.
        if field already exists, old value will be overwritten.
        """
        if not force:
            return await self.update(key, Update.set(field))
        try:
            return await self.update(key, Update.set(field))
        except NotFound:
            return await self.put(key=key, field=field)

    async def remove_field(self, key: str, field_name: str) -> Dict[str, Any]:
        """
        removes a field from an existing key.
        """
        return await self.update(key, Update.remove(field_name))

    async def fetch(self, key: str) -> Dict[str, Any]:
        """
        fetches a single item from deta by key.
        """
        return await self.__route._fetch(base_name=self.name, key=key[0])

    async def multi_fetch(self, *keys: str) -> List[Dict[str, Any]]:
        """
        fetches multiple keys and values from given base.
        """
        return list(await asyncio.gather(*[self.__route._fetch(base_name=self.name, key=k) for k in keys]))

    async def fetch_all(self) -> List[Dict[str, Any]]:
        """
        fetches all key and values from given base.
        """
        return await self.__route._fetch_all(base_name=self.name)

    async def put(
            self,
            key: str,
            field: Field,
            *,
            expire_at: datetime = None,
            expire_after: Union[int, float] = None,
    ) -> Dict[str, Any]:
        """
        adds a field to base with given key.
        if key already exists, old value will be overwritten.
        """
        payload = {"items": [{"key": str(key), field.name: field.value}]}
        if expire_at:
            payload['items'][0][self.__expiry_key] = self.__time_to_expiry(expire_at)
        elif expire_after:
            payload['items'][0][self.__expiry_key] = self.__time_to_expiry(expire_after)
        return await self.__route._put(base_name=self.name, json_data=payload)

    async def put_many(
            self,
            key: str,
            fields: List[Field],
            *,
            expire_at: datetime = None,
            expire_after: Union[int, float] = None,
    ) -> Dict[str, Any]:
        """
        adds multiple field to base with given single key.
        if key already exists, old value will be overwritten.
        """
        data = {field.name: field.value for field in fields}
        data['key'] = str(key)
        if expire_at:
            data[self.__expiry_key] = self.__time_to_expiry(expire_at)
        elif expire_after:
            data[self.__expiry_key] = self.__time_to_expiry(expire_after)
        payload = {"items": [data]}
        return await self.__route._put(base_name=self.name, json_data=payload)

    async def put_bulk(
            self,
            keys: List[str],
            fields: List[List[Field]],
            *,
            expire_ats: List[datetime] = None,
            expire_afters: List[Union[int, float]] = None,
    ) -> Dict[str, Any]:
        """
        adds multiple fields to base with given multiple keys.
        if any key already exists, old value will be overwritten.
        """
        if len(keys) > 25:
            raise ValueError("bulk insert is limited to 25 keys")

        if len(keys) != len(fields):
            raise ValueError("keys and bulk_fields must be the same in length")

        if expire_ats and len(expire_ats) != len(keys):
            raise ValueError("expire_ats and keys must be the same in length")

        if expire_afters and len(expire_afters) != len(keys):
            raise ValueError("expire_afters and keys must be the same in length")

        if expire_ats:
            timer_list = [self.__time_to_expiry(expire_at) for expire_at in expire_ats]
        elif expire_afters:
            timer_list = [self.__time_to_expiry(expire_after) for expire_after in expire_afters]
        else:
            timer_list = None
        form = []
        if timer_list:
            for key, fields, time in zip(keys, fields, timer_list):
                data = {field.name: field.value for field in fields}
                data['key'] = str(key)
                data[self.__expiry_key] = time
                form.append(data)
        else:
            for key, fields in zip(keys, fields):
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

    async def delete_many(self, *keys: str) -> Dict[str, Any]:
        """
        removes multiple keys and their values from base with given keys.
        """
        return await self.__route._delete_many(base_name=self.name, keys=list(keys))

    async def insert(self, key: str, field: Field) -> Dict[str, Any]:
        """
        creates a field to base with given key if any field with same key doesn't exist.
        """
        payload = {"item": {"key": str(key), field.name: field.value}}
        return await self.__route._insert(base_name=self.name, json_data=payload)

    async def insert_many(self, key: str, *fields: Field) -> Dict[str, Any]:
        """
        creates multiple fields to base with given key if any of fields with same key doesn't exist.
        Uses a single call to API.
        """
        payload = {"key": str(key), "item": {field.name: field.value for field in fields}}
        return await self.__route._insert(base_name=self.name, json_data=payload)

    async def update(self, key: str, *updates: Update) -> Dict[str, Any]:
        """
        updates a field only if a field with given key exists.
        """
        payload = {}
        for u in updates:
            payload.update(u._value)
        return await self.__route._update(base_name=self.name, key=key, payload=payload)

    async def query(
            self,
            query: Query,
            *,
            limit: Optional[int] = None,
            last: Optional[str] = None
    ) -> List[Any]:
        """
        queries base with given query.
        """
        return await self.__route._query(base_name=self.name, query=query.payload, last=last, limit=limit)
