import io
from .route import Route
from typing import List, Dict, Optional, Union, Any


class _Drive:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__route = Route(deta)

    async def close(self):
        await self.__route._close()

    async def files(self, limit: Optional[int] = None, prefix: Optional[str] = None) -> List[str]:
        """
        fetches names of files in the drive.
        """
        def get_last(response: dict):
            if response.get('paging') and response.get('paging').get('last'):
                return response['paging']['last']
            return None

        names = []
        if not limit and not prefix:
            ini_resp = await self.__route._fetch_file_list(drive_name=self.name)
            names.extend(ini_resp['names'])
            last = get_last(ini_resp)
            while last:
                resp = await self.__route._fetch_file_list(drive_name=self.name, last=last)
                names.extend(resp['names'])
                last = get_last(resp)
        elif not limit and prefix:
            ini_resp = await self.__route._fetch_file_list(drive_name=self.name, prefix=prefix)
            names.extend(ini_resp['names'])
            last = get_last(ini_resp)
            while last:
                resp = await self.__route._fetch_file_list(drive_name=self.name, last=last, prefix=prefix)
                names.extend(resp['names'])
                last = get_last(resp)
        else:
            resp = await self.__route._fetch_file_list(drive_name=self.name, limit=limit, prefix=prefix)
            names.extend(resp['names'])

        return names

    async def delete(self, file_name: str) -> Dict[str, Any]:
        """
        deletes a file from the drive. if the file is not found it will do nothing.
        """
        return await self.__route._bulk_delete_files(drive_name=self.name, keys=[file_name])

    async def delete_many(self, *file_names: str) -> Dict[str, Any]:
        """
        deletes multiple files from the drive with one request.
        """
        return await self.__route._bulk_delete_files(drive_name=self.name, keys=list(file_names))

    async def upload(
            self,
            file_name: str,
            *,
            path: Optional[str] = None,
            content: Optional[Union[bytes, str, io.BytesIO]] = None
    ) -> Dict[str, Any]:
        """
        uploads a file to the drive with the given name.
        """
        if path and content:
            raise ValueError("file_path and content both are not allowed in same time")

        if not path and not content:
            raise ValueError("path or content is required")

        return await self.__route._push_file(
            drive_name=self.name,
            remote_path=file_name,
            file_path=path,
            content=content
        )

    async def get(self, file_name: str) -> io.BytesIO:
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
