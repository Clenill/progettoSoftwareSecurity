class AppException(Exception):

    def __init__(
        self,
        status_code: int,
        detail: str
    ):
        self.status_code = status_code
        self.detail = detail

        super().__init__(detail)

class UserNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Utente non trovato"
        )


class EmailAlreadyExistsException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Email già registrata"
        )


class PasswordTooLongException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Password troppo lunga"
        )