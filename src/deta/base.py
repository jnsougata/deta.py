import asyncio
from .errors import *
from aiohttp import ClientSession
from typing import Union
from .route import _Route
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .utils import Field, _Update, _Query, Set, Delete


class _Base:
    def __init__(self, name: str, project_key: str, session: ClientSession):
        self.name = name
        self._route = _Route(project_key, session)
        self._expiry_key = '__expires'

    def __str__(self):
        return self.name

    async def close(self):
        return await self._route.close()

    @staticmethod
    def __time_to_expiry(time_value: Union[int, float, datetime]) -> Union[int, float]:
        if isinstance(time_value, datetime):
            return time_value.replace(microsecond=0).timestamp()
        else:
            return (datetime.now() + timedelta(seconds=time_value)).replace(microsecond=0).timestamp()

    async def add_field(self, key: str, *fields: Field) -> Dict[str, Any]:
        return await self.update(key, Set(*fields))

    async def delete_field(self, key: str, *field_names: str) -> Dict[str, Any]:
        return await self.update(key, Delete(*field_names))

    async def get(self, key: str) -> Dict[str, Any]:
        return await self._route.get(self.name, key)

    async def get_multiple(self, *keys: str) -> List[Dict[str, Any]]:
        return list(await asyncio.gather(*[self._route.get(self.name, k) for k in keys]))

    async def records(self) -> List[Dict[str, Any]]:
        return await self._route.fetch_all(self.name)

    async def put(
            self,
            key: str,
            *fields: Field,
            expire_at: datetime = None,
            expire_after: Union[int, float] = None,
    ) -> Dict[str, Any]:
        data = {field.name: field.value for field in fields}
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if key:
            data['key'] = str(key)
        if expire_at:
            payload['items'][0][self._expiry_key] = self.__time_to_expiry(expire_at)
        elif expire_after:
            payload['items'][0][self._expiry_key] = self.__time_to_expiry(expire_after)
        return await self._route.put(self.name, {"items": [data]})

    async def put_multiple(
            self,
            keys: List[str],
            *fields: List[Field],
            expire_ats: List[datetime] = None,
            expire_afters: List[Union[int, float]] = None,
    ) -> Dict[str, Any]:
        assert len(keys) <= 25, "cannot put more than 25 items at once"
        assert len(keys) == len(fields), "keys and fields must be of same length"
        assert not (expire_ats and expire_afters), "cannot use both expire_ats and expire_afters"
        assert len(keys) == len(expire_ats) if expire_ats else True, "keys and expire_ats must be of same length"
        assert len(keys) == len(expire_afters) if expire_afters else True, "keys and expire_afters must be of same length"
        if expire_ats:
            expiry = [self.__time_to_expiry(expire_at) for expire_at in expire_ats]
        elif expire_afters:
            expiry = [self.__time_to_expiry(expire_after) for expire_after in expire_afters]
        else:
            expiry = None
        form = []
        if expiry:
            for key, fields, time in zip(keys, fields, expiry):
                data = {field.name: field.value for field in fields}
                data['key'] = str(key)
                data[self._expiry_key] = time
                form.append(data)
        else:
            for key, fields in zip(keys, fields):
                data = {field.name: field.value for field in fields}
                data['key'] = str(key)
                form.append(data)
        return await self._route.put(self.name, {"items": form})

    async def delete(self, *keys: str) -> Union[Dict[str, Any] | List[Dict[str, Any]]]:
        if len(keys) == 1:
            return await self._route.delete(self.name, keys[0])
        else:
            return await self._route.delete_many(self.name, list(keys))

    async def insert(self, key: str, *fields: Field) -> Dict[str, Any]:
        return await self._route.insert(
            self.name,
            {
                "key": str(key),
                "item": {field.name: field.value for field in fields}
            }
        )

    async def update(self, key: str, *updates: _Update) -> Dict[str, Any]:
        payload = {}
        for u in updates:
            payload.update(**u.value)
        return await self._route.update(self.name, str(key), payload)

    async def fetch(self, *queries: _Query, limit: Optional[int] = None, last: Optional[str] = None) -> List[Any]:
        translated = [q.value for q in queries]
        return await self._route.fetch(self.name, limit, last, translated)
