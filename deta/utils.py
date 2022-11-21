from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Any


def unix_converter(time_value: Union[int, float, datetime]) -> float:
    if isinstance(time_value, datetime):
        return time_value.replace(microsecond=0).timestamp()
    else:
        return (datetime.now() + timedelta(seconds=time_value)).replace(microsecond=0).timestamp()

class Record:
    def __init__(
        self,  
        data: Dict[str, Any] = None,
        *, 
        key: str = None,
        expire_at: datetime = None,
        expire_after: Union[int, float] = None,
    ):
        self.key = key
        self.data = data or {}
        self.expire_at = expire_at
        self.expire_after = expire_after
    
    def __repr__(self) -> str:
        return f"Record({self.key}, {self.name}, {self.value})"
    
    def to_json(self) -> Dict[str, Any]:
        if self.key:
            self.data["key"] = self.key
        if self.expire_at:
            self.data["__expires"] = unix_converter(self.expire_at)
        elif self.expire_after:
            self.data["__expires"] = unix_converter(self.expire_after)
        return self.data

class Updater:

    def __init__(self) -> None:
        self._set = {}
        self._increment = {}
        self. _append = {}
        self._prepend = {}
        self._delete = []
    
    def set(self, field: str, value: Any):
        self._set[field] = value
    
    def increment(self, field: str, value: Union[int, float] = 1):
        self._increment[field] = value
    
    def append(self, field: str, value: List[Any]):
        self._append[field] = value
    
    def prepend(self, field: str, value: List[Any]):
        self._prepend[field] = value
    
    def delete(self, field: str):
        self._delete.append(field)
    
    def to_json(self) -> Dict[str, Any]:
        payload = {}
        if self._set:
            payload["set"] = self._set
        if self._increment:
            payload["increment"] = self._increment
        if self._append:
            payload["append"] = self._append
        if self._prepend:
            payload["prepend"] = self._prepend
        if self._delete:
            payload["delete"] = self._delete
        return payload

class Query:
    def __init__(self):
        self._payload = {}
    
    def equal(self, field: str, value: Any):
        self._payload[field] = value
    
    def not_equal(self, field: str, value: Any):
        self._payload[f"{field}?ne"] = value
    
    def greater_than(self, field: str, value: Any):
        self._payload[f"{field}?gt"] = value
    
    def greater_equal(self, field: str, value: Any):
        self._payload[f"{field}?gte"] = value
    
    def less_than(self, field: str, value: Any):
        self._payload[f"{field}?lt"] = value
    
    def less_equal(self, field: str, value: Any):
        self._payload[f"{field}?lte"] = value
    
    def contains(self, field: str, value: Any):
        self._payload[f"{field}?contains"] = value
    
    def not_contains(self, field: str, value: Any):
        self._payload[f"{field}?not_contains"] = value
    
    def range(self, field: str, start: Union[int, float], end: Union[int, float]):
        self._payload[f"{field}?r"] = [start, end]
    
    def prefix(self, field: str, value: str):
        self._payload[f"{field}?pfx"] = value

    def to_json(self) -> Dict[str, Any]:
        return self._payload
        