from typing import List, Dict, Any, Union


class Field:
    def __init__(self, name: str, value: Union[int, str, bool, float, list, Dict[str, Any]]):
        self.name = name
        self.value = value


class Updater:

    @staticmethod
    def set(fields: List[Field]):
        return {'set': {field.name: field.value for field in fields}}

    @staticmethod
    def increment(fields: List[Field]):
        form = {}
        for filed in fields:
            if isinstance(filed.value, int) or isinstance(filed.value, float):
                form[filed.name] = filed.value
            else:
                raise TypeError('increment value must be int or float')
        return {'increment': form}

    @staticmethod
    def append(fields: List[Field]):
        form = {}
        for filed in fields:
            if isinstance(filed.value, list):
                form[filed.name] = filed.value
            else:
                raise TypeError('append value must be list')

        return {'append': form}

    @staticmethod
    def prepend(fields: List[Field]):
        form = {}
        for filed in fields:
            if isinstance(filed.value, list):
                form[filed.name] = filed.value
            else:
                raise TypeError('prepend value must be list')

        return {'prepend': form}

    @staticmethod
    def remove(fields: List[Field]):
        form = [field.name for field in fields]
        return {'delete': form}
