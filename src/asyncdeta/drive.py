from .route import Route


class _Drive:

    def __init__(self, *, name: str, deta):
        self.name = name
        self.__session = deta.session
        self.__route = Route(deta.token, deta.session)
