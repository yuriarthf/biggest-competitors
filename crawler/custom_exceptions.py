class BadReturnCode(Exception):
    def __init__(self, status_code, message=None):
        self.status_code = status_code
        if not message:
            self.message = f'HTTP request returned status code of {self.status_code}'
        else:
            self.message = message
        super().__init__(self.message)


class InvalidArgument(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
