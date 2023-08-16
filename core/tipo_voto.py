from enum import Enum

class TipoVoto(Enum):
    SIM = 1
    ABSTENÇÃO = 0
    NÃO = -1
    OBSTRUÇÃO = -1 
    ARTIGO_17 = 0
    NONE = 0
    FAVORÁVEL_COM_RESTRIÇÕES = 1 
    BRANCO = 0
    LIBERADO = 0

    @classmethod
    def trat_voto(cls, voto: str) -> int:
        voto_trat = str(voto).upper().replace(' ', '_')
        if voto_trat == 'NAN' or voto_trat == '':
            return None
        return cls[voto_trat].value