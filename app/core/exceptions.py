from app.core.error_codes import ErrorCode

class AppException(Exception):

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: ErrorCode, 
        *args
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

        super().__init__(detail, *args)

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

class ProbabilityNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=404, 
            detail="Probabilità della prova non trovata", 
            error_code=ErrorCode.PROBABILITY_NOT_FOUND
        )

class InvalidProbabilityException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400, 
            detail="Valore di probabilità non valido, deve essere compreso tra 0 e 1", 
            error_code=ErrorCode.INVALID_PROBABILITY
        )

class TransactionFailedException(AppException):

    def __init__(self, *args):
        super().__init__(
            *args, 
            status_code=500, 
            detail="Transazione fallita", 
            error_code=ErrorCode.TRANSACTION_FAILED, 
        )

class FunctionNotFoundException(AppException):

    def __init__(self, name):
        super().__init__(
            name, 
            status_code=503, 
            detail="Funzione non disponibile", 
            error_code=ErrorCode.FUNCTION_NOT_FOUND, 
        )

class VisitNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            status_code=404, 
            detail="Visita non trovata", 
            error_code=ErrorCode.VISIT_NOT_FOUND
        )

class DuplicateVisitException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400, 
            detail="Visita già inserita", 
            error_code=ErrorCode.DuplicateVisit
        )

class DuplicateEvidenceException(AppException):

    def __init__(self):
        super().__init__(
            status_code=400, 
            detail="Prova già inserita", 
            error_code=ErrorCode.DuplicateEvidence
        )

