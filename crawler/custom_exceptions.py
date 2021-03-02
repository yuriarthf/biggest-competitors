class BadReturnCode(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        self.message = f'HTTP request returned status code of {self.status_code}'
        super().__init__(self.message)


class InvalidArgument(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
