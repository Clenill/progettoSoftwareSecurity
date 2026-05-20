
from enum import Enum
from app.enum.ruolo import ruolo

class TipoProva(str, Enum):
    SINTOMI = 'sintomi'
    ATTREZZATURA = 'attrezzatura'
    PRESCRIZIONE = 'prescrizione'
    CONFERMA = 'conferma'
    GPS = 'gps'

PROVE_RUOLI = {
    ruolo.PAZIENTE: { TipoProva.CONFERMA }, 
    ruolo.MEDICO: {
        TipoProva.SINTOMI, 
        TipoProva.ATTREZZATURA, 
        TipoProva.PRESCRIZIONE, 
        TipoProva.GPS
    }
}

