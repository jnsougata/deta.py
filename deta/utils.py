from __future__ import annotations
from typing import List, Dict, Any, Union, Optional


class Field:
    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value

    def dict(self) -> Dict[str, Any]:
        return {self.name: self.value}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> List[Field]:
        return [cls(name=k, value=v) for k, v in data.items()]


class _Update:

    def __init__(self, payload: Dict[str, Any]):
        self.value = payload


class Set(_Update):
    def __init__(self, *fields: Field):
        super().__init__({'set': {field.name: field.value for field in fields}})


class Increment(_Update):
    def __init__(self, *fields: Field):
        form = {}
        for field in fields:
            if isinstance(field.value, int) or isinstance(field.value, float):
                form.update(field.dict())
            else:
                raise TypeError('increment value must be int or float')
        super().__init__({'increment': form})


class Append(_Update):
    def __init__(self, *fields: Field):
        form = {}
        for field in fields:
            if isinstance(field.value, list):
                form.update(field.dict())
            else:
                raise TypeError('append value must be list')
        super().__init__({'append': form})


class Prepend(_Update):
    def __init__(self, *fields: Field):
        form = {}
        for field in fields:
            if isinstance(field.value, list):
                form.update(field.dict())
            else:
                raise TypeError('prepend value must be list')
        super().__init__({'prepend': form})


class Delete(_Update):
    def __init__(self, *fields: str):
        super().__init__({'delete': list(fields)})


class _Query:

    def __init__(self, payload: Union[Dict[str, Any]]):
        self.value = payload


class KeyQuery(_Query):
    def __init__(self, key: str):
        super().__init__({'key': key})


class PrefixQuery(_Query):
    def __init__(self, prefix: str):
        super().__init__({'key?pfx': prefix})


class EqualsQuery(_Query):
    def __init__(self, field: str, value: Any):
        super().__init__({field: value})


class NotEqualsQuery(_Query):
    def __init__(self, field: str, value: Any):
        super().__init__({f'{field}?ne': value})


class GreaterThanQuery(_Query):
    def __init__(self, field: str, value: Any):
        super().__init__({f'{field}?gt': field})


class GreaterEqualsQuery(_Query):
    def __init__(self, field: str, value: Any):
        super().__init__({f'{field}?gte': value})


class LessThanQuery(_Query):
    def __init__(self, field: str, value: Any):
        super().__init__({f'{field}?lt': value})


class LessEqualsQuery(_Query):
    def __init__(self, field: str, value: Any):
        super().__init__({f'{field}?lte': value})


class InRangeQuery(_Query):
    def __init__(self, field: str, value: List[Union[int, float]]):
        super().__init__({f'{field.name}?r': value})


class ContainsQuery(_Query):
    def __init__(self, field: str, value: Union[List[Any], str]):
        super().__init__({f'{field}?contains': value})


class NotContainsQuery(_Query):
    def __init__(self, field: str, value: Union[List[Any], str]):
        super().__init__({f'{field}?not_contains': value})


class StartsWithQuery(_Query):
    def __init__(self, field: str, value: str):
        super().__init__({f'{field}?pfx': value})


class AND(_Query):
    def __init__(self, *queries: _Query):
        super().__init__({key: value for query in queries for key, value in query.value.items()})


class OR:
    def __init__(self, *batches: List[_Query]):
        self.value = []
        children = []
        reference = [[i] for i in batches[0]]
        for batch in batches[1:]:
            for i in batch:
                for r in reference:
                    children.append(r + [i])
            reference = children
            children = []
        self.value = list(set([AND(*r) for r in reference]))
