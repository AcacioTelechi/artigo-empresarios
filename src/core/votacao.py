"Voting-related objects."
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

VOTOS_DE_PARA = {"Sim": 1, "Não": -1, "Obstrução": -1}


@dataclass
class Votacao:
    "Voting representation."
    praca: str
    id_votacao: str
    id_prop: str
    data_hora_registro: datetime
    sigla_orgao: str
    descricao: str
    aprovacao: bool

    def __post_init__(self):
        if isinstance(self.data_hora_registro, str):
            self.data_hora_registro = datetime.strptime(
                self.data_hora_registro, "%Y-%m-%dT%H:%M:%S"
            )


@dataclass
class Voto:
    "Vote representation."
    praca: str
    id_parl: str
    sigla_partido: str
    id_votacao: str
    voto: str
    voto_trat: int | None = None

    def __post_init__(self):
        if not self.voto_trat:
            if self.voto in VOTOS_DE_PARA.keys():
                self.voto_trat = VOTOS_DE_PARA[self.voto]
            else:
                self.voto_trat = 0


@dataclass
class OrientacaoVoto:
    "Vote orientation representation."
    orientacao_voto: str
    cod_tipo_lideranca: str
    sigla_partido_bloco: str
    cod_partido_bloco: str
    id_votacao: str

    def __post_init__(self):
        if self.orientacao_voto in VOTOS_DE_PARA.keys():
            self.voto_trat = VOTOS_DE_PARA[self.orientacao_voto]
        else:
            self.voto_trat = 0


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
    def trat_voto(cls, voto: str) -> int | None:
        voto_trat = str(voto).upper().replace(" ", "_")
        if voto_trat == "NAN" or voto_trat == "":
            return None
        return cls[voto_trat].value
