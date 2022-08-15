class NotFound(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BadRequest(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class KeyConflict(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
