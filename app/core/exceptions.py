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

class VisitException(Exception):

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
class UserNotAuthorizedException(AppException):

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Autorizzazione mancante",
            error_code=ErrorCode.USER_NOT_AUTHORIZED
        )

class InvalidCredentials(AppException):

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Credenziali non valide",
            error_code=ErrorCode.INVALID_CREDENTIAL
        )

class MissingVisitDetailsException(AppException):
    DEFAULT_DETAIL = "Qualcosa è andato storto nella richiesta"

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=400,
            detail=detail or self.DEFAULT_DETAIL,
            error_code=ErrorCode.MISSING_VISIT_DETAILS
        )

class UserNotActive(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Utente non attivo",
            error_code=ErrorCode.NOT_ACTIVE_USER
        )

class UserAlreadyActive(AppException):
    
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Utente già attivo.",
            error_code=ErrorCode.USER_IS_ACTIVE
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

class InvalidDoctorIdException(AppException):

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Id non corrisponde all'id Medico della visita",
            error_code=ErrorCode.INVALID_DOCTOR_ID
        )

class InvalidUserRoleException(AppException):
    DEFAULT_DETAIL= "Ruolo non corrisponde all'Id."

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=404,
            detail=detail or self.DEFAULT_DETAIL,
            error_code=ErrorCode.INVALID_ROLE
        )
class InvalidVisitDateException(AppException):

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Data visita non valida, controllare il formato o che non sia passata",
            error_code=ErrorCode.INVALID_DATE
        )

class VisitAlreadyConfirmedException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="La visita è già stata confermata",
            error_code=ErrorCode.VISIT_ALREADY_CONFIRMED
        )

class VisitNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Visita non trovata",
            error_code=ErrorCode.VISIT_NOT_FOUND
        )

class VisitAlreadyOccurredException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="La visita è già avvenuta e non può essere cancellata",
            error_code=ErrorCode.VISIT_ALREADY_OCCURRED
        )

class VisitTimeConflictException(VisitException):

    def __init__(self):
        super().__init__(
            status_code=409,
            detail="Esiste già una visita nell'intervallo richiesto",
            error_code=ErrorCode.VISIT_TIME_CONFLICT
        )