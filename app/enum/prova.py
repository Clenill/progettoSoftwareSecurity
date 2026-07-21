
from enum import Enum
from app.enum.ruolo import ruolo

class TipoProva(str, Enum):
    SINTOMI = 'sintomi'
    ATTREZZATURA = 'attrezzatura'
    PRESCRIZIONE = 'prescrizione'
    CONFERMA = 'conferma'
    GPS = 'gps'

# mappa le prove ai loro indici sequenziali e gli indici alle prove
ID_PROVE = dict(zip(
    list(TipoProva) + list(range(len(TipoProva))), 
    list(range(len(TipoProva))) + list(TipoProva)
))

PROVE_RUOLI = {
    ruolo.PAZIENTE: { TipoProva.CONFERMA }, 
    ruolo.MEDICO: {
        TipoProva.SINTOMI, 
        TipoProva.ATTREZZATURA, 
        TipoProva.PRESCRIZIONE, 
        TipoProva.GPS
    },
    ruolo.AUTORITY: {
        TipoProva.SINTOMI, 
        TipoProva.ATTREZZATURA, 
        TipoProva.PRESCRIZIONE, 
        TipoProva.GPS,
        TipoProva.CONFERMA
    }
}

