from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.core.security import has_role_in
from app.core.exceptions import UserNotAuthorizedException, InvalidCredentials
from app.models.schemas import VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate, PriorUpdate, LikelihoodUpdate, ContractAccountInfoRequest, UserResponse
from app.enum.ruolo import ruolo
from app.enum.prova import TipoProva, PROVE_RUOLI, ID_PROVE
from app.service.visit_service import VisitService
from app.service.user_service import UserService
from app.service.contract_service import ContractService

from app.core.config import CONTRACT, SCALE

from uuid import UUID

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# La chiamata va triggerata e gli si deve passare id medico e paziente
@router.post("/newvisit", response_model=VisitResponse)
async def admin_create_visit(
    visit: VisitCreate,
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])),
    db: AsyncSession = Depends(get_db)
):
    visit = await VisitService.admin_create_visit(
        visit,
        db,
        current_user, 
        commit=False
    )
    #await ContractService.add_visit(current_user, visit)
    await db.commit()
    await db.refresh(visit)
    return visit

@router.get("/visiteutente/{id}", response_model=list[VisitResponse])
async def get_user_visits(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_user_by_id(id, db)
    return await VisitService.get_visits(user, db)

@router.put("/visits/{id}/confirm")
async def confirm_visit(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visit = await VisitService.confirm_visit(db, id, commit=False)
    await ContractService.add_visit(current_user, visit)
    await db.commit()
    await db.refresh(visit)
    return visit

@router.get("/allvisits", response_model=list[VisitResponse])
async def admin_get_all_visits(
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visits = await VisitService.get_visits(None, db)
    (bc_visits, probabilita_visite) = await ContractService.get_visits()
    for (visit, bc_visit, probabilita) in zip(visits, bc_visits, probabilita_visite):
        visit.probabilita = probabilita
    return visits

@router.get("/dettagliovisita/{id}", response_model=VisitResponse)
async def admin_get_visit(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visit = await VisitService.get_visit_by_id(id, None, db)
    (bc_visit, probabilita) = await ContractService.get_visit(id)
    # TODO: controlla coerenza tra gli UUID dello smart contract e quelli del DB
    visit.probabilita = probabilita
    return visit

@router.put("/updatevisits/{id}", response_model=VisitResponse)
async def edit_visit(
    visit: VisitUpdate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visit = await VisitService.edit_visit(id, visit, None, db, commit=False)
    await ContractService.edit_visit(current_user, visit)
    await db.commit()
    await db.refresh(visit)
    return visit

@router.delete("/deletevisit/{id}")
async def delete_visit(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visit = await VisitService.get_visit_by_id(id, None, db)
    if visit.confermata:
        await ContractService.cancel_visit(current_user, id)
    else:
        await VisitService.delete_visit(id, current_user, db, commit=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
@router.post("/addevidence/{id}")
async def add_evidence(
    evidence: EvidenceCreate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    await VisitService.add_evidence(id, evidence.tipo, None, db, commit=False)
    await ContractService.add_evidence(current_user, id, evidence.tipo, evidence.valore)
    await db.commit()
    return { 
        "message": "Prova aggiunta con successo",
        "visit_id": id,
        "evidence_type": evidence.tipo, 
        "valore": evidence.valore
        }

@router.post("/activeuser/{id}")
async def active_new_user(
    id:UUID,
    current_user:User = Depends(has_role_in([ruolo.AUTORITY])),
    db: AsyncSession = Depends(get_db)
):
    await UserService.active_user(id, db)
    return { "message": "Utente attivato!" }

@router.get("/probabilita/priori")
async def get_prior(current_user: User = Depends(has_role_in([ruolo.AUTORITY]))):
    prior = await ContractService.get_prior()
    return {
        "value": prior
    }

@router.post("/probabilita/priori")
async def update_prior(
    req: PriorUpdate, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    await ContractService.set_prior(req.value)
    return { "message": "probabilità aggiornata" }

@router.get("/probabilita/prove")
async def get_likelihoods(
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    info_prove = await ContractService.get_likelihoods()
    return info_prove

@router.get("/probabilita/{tipo}")
async def get_likelihood(
    tipo: TipoProva, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    info = await ContractService.get_likelihood(tipo)
    return info

@router.post("/probabilita/prova")
async def update_likelihood(
    req: LikelihoodUpdate, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    await ContractService.set_likelihood(
        req.tipo, 
        req.ptrue, 
        req.pfalse
    )
    return { "message": "probabilità aggiornata" }

@router.delete("/probabilita/{tipo}")
async def remove_likelihood(
    tipo: TipoProva, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    await ContractService.remove_likelihood(tipo)
    return { "message": "probabilità rimossa" }

@router.post("/contract/grantpermissions")
async def grant_contract_permissions(
    account: ContractAccountInfoRequest, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    await ContractService.add_permissioned_account(account.address)
    return { "message": "permessi aggiunti" }

@router.delete("/contract/revokepermissions")
async def revoke_contract_permissions(
    account: ContractAccountInfoRequest, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY]))
):
    await ContractService.remove_permissioned_account(account.address)
    return { "message": "permessi rimossi" }

@router.get("/allusers", response_model=list[UserResponse])
async def get_users(
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_users(db)

