from aiohttp import ClientResponse
from typing import Any, Dict


__all__ = ['NotFound', 'BadRequest', 'KeyConflict', '_raise_or_return', 'PayloadTooLarge']


class NotFound(Exception):
    """
    Raised when a resource is not found
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BadRequest(Exception):
    """
    Raised when a request body is invalid
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class KeyConflict(Exception):
    """
    Raised when a key already exists in the base
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class PayloadTooLarge(Exception):
    """
    Raised when the payload size exceeds the limit of 10MB
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


async def _raise_or_return(response: ClientResponse, ok: int = 200) -> Dict[str, Any]:
    if response.status == ok:
        return await response.json()
    else:
        if response.status == 413:
            raise PayloadTooLarge("Payload size is exceeds the limit of 10MB")
        if response.status == 404:
            raise NotFound("Resource not found")
        message = ".".join((await response.json())['errors'])
        if response.status == 400:
            raise BadRequest(message)
        elif response.status == 409:
            raise KeyConflict(message)
        else:
            raise Exception(message)
