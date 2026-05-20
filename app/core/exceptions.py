from app.core.error_codes import ErrorCode

class AppException(Exception):

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: ErrorCode
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

        super().__init__(detail)

class UserNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Utente non trovato",
            error_code=ErrorCode.USER_NOT_FOUND
        )


class EmailAlreadyExistsException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Email già registrata",
            error_code=ErrorCode.EMAIL_ALREADY_EXISTS
        )


class PasswordTooLongException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Password troppo lunga",
            error_code=ErrorCode.PASSWORD_TOO_LONG
        )