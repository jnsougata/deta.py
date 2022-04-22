import io

from .route import Route
from typing import List, Dict, Optional, Union, Any


class _Drive:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__route = Route(deta)

    async def files(self, limit: int = None) -> Dict[str, Any]:
        return await self.__route._fetch_file_list(drive_name=self.name, limit=limit)

    async def delete(self, file_name: str) -> Dict[str, Any]:
        return await self.__route._bulk_delete_files(drive_name=self.name, keys=[file_name])

    async def delete_many(self, file_names: List[str]) -> Dict[str, Any]:
        return await self.__route._bulk_delete_files(drive_name=self.name, keys=file_names)

    async def upload(
            self,
            *,
            file_name: str,
            local_path: Optional[str] = None,
            content: Optional[Union[bytes, str]] = None
    ) -> Dict[str, Any]:
        return await self.__route._push_file(
            drive_name=self.name,
            remote_path=file_name,
            local_path=local_path,
            content=content
        )

