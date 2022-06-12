import io
from .route import Route
from typing import List, Dict, Optional, Union, Any


class _Drive:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__route = Route(deta)

    async def files(self, limit: int = None) -> List[str]:
        """
        fetches names of files in the drive.
        """
        if limit is None:
            container = []

            async def recurse(last: Optional[str]):
                data = await self.__route._fetch_file_list(drive_name=self.name, limit=None)
                paging = data.get('paging')
                if paging:
                    container.extend(data['names'])
                    await recurse(paging.get('last'))
                else:
                    container.extend(data['names'])
                    return container
            return await recurse(None)
        else:
            return (await self.__route._fetch_file_list(drive_name=self.name, limit=limit))['names']

    async def delete(self, file_name: str) -> Dict[str, Any]:
        """
        deletes a file from the drive. if the file is not found it will do nothing.
        """
        return await self.__route._bulk_delete_files(drive_name=self.name, keys=[file_name])

    async def delete_many(self, file_names: List[str]) -> Dict[str, Any]:
        """
        deletes multiple files from the drive with one request.
        """
        return await self.__route._bulk_delete_files(drive_name=self.name, keys=file_names)

    async def upload(
            self,
            *,
            file_name: str,
            local_path: Optional[str] = None,
            content: Optional[Union[bytes, str]] = None
    ) -> Dict[str, Any]:
        """
        uploads a file to the drive with the given name.
        """
        return await self.__route._push_file(
            drive_name=self.name, remote_path=file_name, local_path=local_path, content=content
        )

    async def download(self, file_name: str) -> io.BytesIO:
        """
        downloads a file from the drive with the given name.
        """
        stream = await self.__route._pull_file(drive_name=self.name, remote_path=file_name)
        buffer = b""

        async for data, end_of_http_chunk in stream.content.iter_chunks():
            buffer += data
            if end_of_http_chunk:
                buffer = b""
        return io.BytesIO(buffer)
