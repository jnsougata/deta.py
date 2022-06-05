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
    def remove(cls, fields: List[Field]):
        return cls({'delete': [field.name for field in fields]})


class Query:

    def __init__(self, payload: Any):
        self._value = payload

    @classmethod
    def equals(cls, key: str, value: Any):
        return cls({key: value})

    @classmethod
    def not_equals(cls, key: str, value: Any):
        return cls({f'{key}?ne': value})

    @classmethod
    def greater_than(cls, key: str, value: Union[int, float]):
        return cls({f'{key}?gt': value})

    @classmethod
    def greater_equals(cls, key: str, value: Union[int, float]):
        return cls({f'{key}?gte': value})

    @classmethod
    def less_than(cls, key: str, value: Union[int, float]):
        return cls({f'{key}?lt': value})

    @classmethod
    def less_equals(cls, key: str, value: Union[int, float]):
        return cls({f'{key}?lte': value})

    @classmethod
    def in_range(cls, key: str, value: Union[int, float]):
        return cls({f'{key}?r': value})

    @classmethod
    def contains(cls, key: str, value: Union[str, List[str]]):
        return cls({f'{key}?contains': value})

    @classmethod
    def not_contains(cls, key: str, value: Union[str, List[str]]):
        return cls({f'{key}?not_contains': value})

    @classmethod
    def starts_with(cls, key: str, value: Union[str, List[str]]):
        return cls({f'{key}?pfx': value})
