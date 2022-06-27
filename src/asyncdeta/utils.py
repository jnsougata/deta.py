from __future__ import annotations
from typing import List, Dict, Any, Union, Optional


class Field:
    def __init__(self, name: str, value: Optional[Union[int, str, bool, float, list, Dict[str, Any]]]):
        self.name = name
        self.value = value


def dict_to_field(payload: Dict[str, Any]) -> List[Field]:
    return [Field(key, value) for key, value in payload.items()]


class Update:

    def __init__(self, payload: Any):
        self._value = payload

    @classmethod
    def set(cls, fields: List[Field]):
        return cls({'set': {field.name: field.value for field in fields}})

    @classmethod
    def increment(cls, fields: List[Field]):
        form = {}
        for filed in fields:
            if isinstance(filed.value, int) or isinstance(filed.value, float):
                form[filed.name] = filed.value
            else:
                raise TypeError('increment value must be int or float')
        return cls({'increment': form})

    @classmethod
    def append(cls, fields: List[Field]):
        form = {}
        for filed in fields:
            if isinstance(filed.value, list):
                form[filed.name] = filed.value
            else:
                raise TypeError('append value must be list')

        return cls({'append': form})

    @classmethod
    def prepend(cls, fields: List[Field]):
        form = {}
        for filed in fields:
            if isinstance(filed.value, list):
                form[filed.name] = filed.value
            else:
                raise TypeError('prepend value must be list')

        return cls({'prepend': form})

    @classmethod
    def remove(cls, field_names: List[str]):
        return cls({'delete': [fields]})


class Query:

    def __init__(self, payload: Union[List[Dict[str, Any]], Dict[str, Any]]):
        if isinstance(payload, list):
            self._data = {'query': payload}
        else:
            self._data = {'query': [payload]}

    @classmethod
    def primary_key(cls, key: Optional[str] = None, *, prefix: Optional[str] = None):
        if prefix and key:
            raise ValueError('prefix and key cannot be used together')
        elif key:
            return cls({'key': key})
        elif prefix:
            return cls({"key?pfx": prefix})
        else:
            raise ValueError('key or prefix must be given and cannot be both None or empty string')

    @classmethod
    def equals(cls, field: Field):
        return cls({field.name: field.value})

    @classmethod
    def not_equals(cls, field: Field):
        return cls({f'{field.name}?ne': field.value})

    @classmethod
    def greater_than(cls, filed: Field):
        return cls({f'{filed.name}?gt': filed.value})

    @classmethod
    def greater_equals(cls, field: Field):
        return cls({f'{field.name}?gte': field.value})

    @classmethod
    def less_than(cls, field: Field):
        return cls({f'{field.name}?lt': field.value})

    @classmethod
    def less_equals(cls, field: Field):
        return cls({f'{field.name}?lte': field.value})

    @classmethod
    def in_range(cls, field: Field):
        return cls({f'{field.name}?r': field.value})

    @classmethod
    def contains(cls, field: Field):
        return cls({f'{field.name}?contains': field.value})

    @classmethod
    def not_contains(cls, field: Field):
        return cls({f'{field.name}?not_contains': field.value})

    @classmethod
    def starts_with(cls, field: Field):
        return cls({f'{field.name}?pfx': field.value})

    @classmethod
    def do_and(cls, *queries: Query):
        return cls({k: v for q in queries for k, v in q._data.items()})

    @classmethod
    def do_or(cls, *queries: Query):
        return cls([q._data['query'][0] for q in queries])
