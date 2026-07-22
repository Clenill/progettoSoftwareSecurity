
from itertools import starmap
from uuid import UUID
from web3.exceptions import ContractLogicError
from app.repositories.contract_repository import ContractRepository
from app.core.config import CONTRACT, SCALE, W3_ACCOUNT, Web3, w3
from app.db.models import User, Visit
from app.enum.prova import TipoProva, ID_PROVE
from app.core.exceptions import *
from typing import Any

class ContractService:

    @staticmethod
    def extract_visit_data(visit_data):
        visit = dict(starmap(
            lambda i,name: (name, visit_data[i]), 
            enumerate(['id', 'physician', 'patient', 'active', 'posterior', 'evidences'])
        ))
        visit['id'] = UUID(bytes=visit['id'])
        visit['posterior'] = visit['posterior'] / SCALE
        return visit

    @staticmethod
    def visit_hash(visit: Visit):
        types = ['bytes16', 'bytes16', 'bytes16']
        values = [
            visit.id.bytes, 
            visit.medico.bytes, 
            visit.paziente.bytes
        ]

        return Web3.keccak(
            w3.codec.encode(types, values)
        )

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
        prior = Web3.to_int(prior)
        
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
        visit: Any = None
        try:
            visit = await ContractRepository.call_function(
                CONTRACT, 
                "getVisit", 
                id.bytes
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "VisitNotFound":
                raise VisitNotFoundException()
            elif error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()
        return visit

    @staticmethod
    async def get_visits_in(ids: list[UUID]):
        try:
            ids_bytes = list(map(lambda id: id.bytes, ids))
            visits = await ContractRepository.call_function(
                CONTRACT, 
                "getVisits", 
                ids_bytes
            )
            visits = list(map(lambda v: ContractService.extract_visit_data(v), visits))
            return dict(map(lambda v: (v['id'], v), visits))
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()

    @staticmethod
    async def get_visits_paged(offset: int, size: int):
        result:dict[Any, dict[Any, Any]] = dict()
        try:
            visits = await ContractRepository.call_function(
                CONTRACT, 
                "getVisitsPaged", 
                offset, 
                size
            )
            visits = list(map(lambda v: ContractService.extract_visit_data(v), visits))
            result = dict(map(lambda v: (v['id'], v), visits))
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "LikelihoodNotFound":
                raise ProbabilityNotFoundException()
            
        return result

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
                raise VisitAlreadyConfirmedException()

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
    async def add_evidence(current_user: User, id: UUID, tipo: TipoProva, valore: bool):
        evidence_id = ID_PROVE[tipo]
        try:
            await ContractRepository.call_function(
                CONTRACT, 
                "addEvidence", 
                current_user.id.bytes, 
                id.bytes, 
                evidence_id, 
                valore, 
                use_transaction=True
            )
        except ContractLogicError as e:
            error = ContractRepository._get_error_name(CONTRACT, e)
            if error == "VisitNotFound":
                raise VisitNotFoundException()
            elif error == "DuplicateEvidence":
                raise EvidenceAlreadyAddedException()

