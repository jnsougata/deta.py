from typing import List, Dict, Any, Union


class Field:
    def __init__(self, name: str, value: Union[int, str, bool, float, list, Dict[str, Any]]):
        self.name = name
        self.value = value


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
        return clas({'increment': form})

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
        form = [field.name for field in fields]
        return cls({'delete': form})


def dict_to_field(payload: Dict[str, Any]) -> List[Field]:
    return [Field(key, value) for key, value in payload.items()]
