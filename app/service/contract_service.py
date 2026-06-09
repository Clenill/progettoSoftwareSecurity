
from app.repositories.contract_repository import ContractRepository
from app.core.config import CONTRACT, SCALE, W3_ACCOUNT, Web3
from app.db.models import User, Visit
from app.enum.prova import TipoProva, ID_PROVE
from uuid import UUID
from app.core.exceptions import *
from web3.exceptions import ContractLogicError

class ContractService:

    @staticmethod
    async def add_permissioned_account(account_address: str):
        await ContractRepository.call_function(
            CONTRACT, 
            "addPermissionedAccount", 
            account_address, 
            use_transaction=True
        )

    @staticmethod
    async def remove_permissioned_account(account_address: str):
        current_account = Web3.to_checksum_address(W3_ACCOUNT.address)
        target_account = Web3.to_checksum_address(account_address)
        if current_account != target_account:
            # temporaneo: si può rimuovere solo sé stessi
            raise UserNotAuthorizedException()
        await ContractRepository.call_function(
            CONTRACT, 
            "removePermissionedAccount", 
            account_address, 
            use_transaction=True
        )

    @staticmethod
    async def get_prior():
        prior = await ContractRepository.call_function(
            CONTRACT, 
            "getFactPrior"
        )
        return prior / SCALE

    @staticmethod
    async def set_prior(value: float):
        await ContractRepository.call_function(
            CONTRACT, 
            "setFactPrior", 
            int(value * SCALE), 
            use_transaction=True
        )

    @staticmethod
    async def get_likelihood(tipo: TipoProva):
        evidence_id = ID_PROVE[tipo]
        try:
            info = await ContractRepository.call_function(
                CONTRACT, 
                "getLikelihood", 
                evidence_id
            )
            return {
                "tipo": ID_PROVE[info[0]], 
                "ptrue": info[1] / SCALE, 
                "pfalse": info[2] / SCALE
            }
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            print('CONTRACT ERROR:', error)
            if error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()

    @staticmethod
    async def set_likelihood(tipo: TipoProva, ptrue: float, pfalse: float):
        evidence_id = ID_PROVE[tipo]
        await ContractRepository.call_function(
            CONTRACT, 
            "setLikelihood", 
            (evidence_id, int(ptrue * SCALE), int(pfalse * SCALE), True), 
            use_transaction=True
        )

    @staticmethod
    async def remove_likelihood(tipo: TipoProva):
        evidence_id = ID_PROVE[tipo]
        try:
            await ContractRepository.call_function(
                CONTRACT, 
                "removeLikelihood", 
                evidence_id, 
                use_transaction=True
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()

    @staticmethod
    async def get_likelihoods():
        info_prove = await ContractRepository.call_function(
            CONTRACT, 
            "getLikelihoods"
        )
        return list(
            map(
                lambda info: { "tipo": ID_PROVE[info[0]], "ptrue": info[1] / SCALE, "pfalse": info[2] / SCALE }, 
                info_prove
            )
        )

    @staticmethod
    async def get_visit(id: UUID):
        try:
            (visit, probabilita) = await ContractRepository.call_function(
                CONTRACT, 
                "getVisit", 
                id.bytes
            )
            return visit, probabilita / SCALE
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "VisitNotFound":
                raise VisitNotFoundException()
            elif error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()

    @staticmethod
    async def get_visits():
        try:
            (visits, probabilita) = await ContractRepository.call_function(
                CONTRACT, 
                "getVisits"
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()
        return visits, list(map(lambda p: p / SCALE, probabilita))

    @staticmethod
    async def add_visit(current_user: User, visit: Visit):
        try:
            await ContractRepository.call_function(
                CONTRACT, 
                "addVisit", 
                current_user.id.bytes, 
                visit.id.bytes, 
                visit.medico.bytes, 
                visit.paziente.bytes, 
                use_transaction=True
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "DuplicateVisit":
                raise VisitAlreadyAddedException()

    @staticmethod
    async def cancel_visit(current_user: User, id: UUID):
        try:
            await ContractRepository.call_function(
                CONTRACT, 
                "cancelVisit", 
                current_user.id.bytes, 
                id.bytes, 
                use_transaction=True
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "VisitNotFound":
                raise VisitNotFoundException()

    @staticmethod
    async def edit_visit(current_user: User, visit: Visit):
        try:
            await ContractRepository.call_function(
                CONTRACT, 
                "editVisit", 
                current_user.id.bytes, 
                visit.id.bytes, 
                visit.medico.bytes, 
                visit.paziente.bytes, 
                use_transaction=True
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "VisitNotFound":
                raise VisitNotFoundException()

    @staticmethod
    async def add_evidence(current_user: User, id: UUID, tipo: TipoProva):
        evidence_id = ID_PROVE[tipo]
        try:
            await ContractRepository.call_function(
                CONTRACT, 
                "addEvidence", 
                current_user.id.bytes, 
                id.bytes, 
                evidence_id, 
                use_transaction=True
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "VisitNotFound":
                raise VisitNotFoundException()
            elif error == "DuplicateEvidence":
                raise EvidenceAlreadyAddedException()

