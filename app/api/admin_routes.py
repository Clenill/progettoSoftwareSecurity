from fastapi import APIRouter, Depends, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User, Visit, Evidence
from app.core.security import has_role_in
from app.core.exceptions import UserNotAuthorizedException, InvalidCredentials
from app.models.schemas import VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate, PriorUpdate, LikelihoodUpdate, ContractAccountInfoRequest, UserResponse
from app.core.re_monitor import admin_monitor
from app.enum.ruolo import ruolo
from app.enum.prova import TipoProva, PROVE_RUOLI, ID_PROVE
from app.service.visit_service import VisitService
from app.service.user_service import UserService
from app.service.contract_service import ContractService

from app.core.config import CONTRACT, SCALE

from datetime import datetime
from uuid import UUID, uuid4

router = APIRouter(
    prefix="/admin",
    tags=["Admin"], 
    dependencies=[Depends(admin_monitor)]
)

# La chiamata va triggerata e gli si deve passare id medico e paziente
@router.post("/newvisit", response_model=VisitResponse)
async def admin_create_visit(
    visit: VisitCreate,
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])),
    db: AsyncSession = Depends(get_db)
):
    visita = await VisitService.admin_create_visit(
        visit,
        db,
        current_user, 
        commit=False
    )
    #await ContractService.add_visit(current_user, visit)
    await db.commit()
    await db.refresh(visita)
    return visita

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

#@router.get("/allvisits", response_model=list[VisitResponse])
@router.get("/unconfirmed-visits", response_model=list[VisitResponse])
async def admin_get_all_visits_unconfirmed(
    page: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, le=100), 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    visits = await VisitService.get_unconfirmed_visits_paged(offset, size, db)
    return visits

@router.get("/sc-visits", response_model=list[VisitResponse])
async def admin_get_all_visits(
    page: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, le=100), 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * size
    sc_visits = await ContractService.get_visits_paged(offset, size)
    visits = await VisitService.get_visits_in(list(sc_visits.keys()), db, as_dict=True)
    # Copia le probabilità dalle visite dello smart contract
    for v in visits.values():
        if v.id in sc_visits:
            v.probabilita = sc_visits[v.id]['posterior']
        else:
            v.probabilita = None

    # Reinserisce le visite presenti nello smart contract ma non nel DB
    for id,v in sc_visits.items():
        if id not in visits:
            visits[id] = Visit(
                id=id, 
                paziente=UUID(bytes=v['patient']), 
                medico=UUID(bytes=v['physician']), 
                timestamp=datetime.fromisoformat('0001-01-01 00:00:00.000Z'), 
                confermata=v['active'], 
                prove=[Evidence(
                    visita=id, 
                    tipo=ID_PROVE[e[0]], 
                    valore=e[1], 
                ) for e in v['evidences']]
            )
            visits[id].probabilita = v['posterior']

    return list(visits.values())

@router.get("/dettagliovisita/{id}", response_model=VisitResponse)
async def admin_get_visit(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visit = await VisitService.get_visit_by_id(id, None, db)
    (bc_visit, probabilita) = await ContractService.get_visit(id)
    visit_hash = ContractService.visit_hash(visit)
    # if bc_hash[0] != visit_hash: print('visit mismatch')
    visit.probabilita = probabilita
    return visit

@router.put("/updatevisits/{id}", response_model=VisitResponse)
async def edit_visit(
    visit: VisitUpdate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    visita = await VisitService.edit_visit(id, visit, None, db, commit=False)
    await ContractService.edit_visit(current_user, visita)
    await db.commit()
    await db.refresh(visita)
    return visita

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
    await VisitService.add_evidence(id, evidence.tipo, evidence.valore, None, db, commit=False)
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

