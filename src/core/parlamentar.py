"Representations of parlamentar objects."

from dataclasses import dataclass, field
from datetime import datetime
import json

# from typing import Self
from enum import auto


@dataclass
class Parlamentar:
    "Representation of a parlamentar."
    id_parl: str
    nome: str
    sigla_partido: str
    sigla_uf: str
    is_active: bool
    praca: str

    def __post_init__(self):
        if isinstance(self.id_parl, int):
            self.id_parl = str(int(self.id_parl))


@dataclass
class ParlamentarDetalhes:
    "Representation of a parlamentar details."
    id_parl: str
    nome: str
    nome_civil: str
    cpf: str
    sexo: str
    data_nascimento: datetime
    data_falecimento: datetime
    uf_nascimento: str
    municipio_nascimento: str
    escolaridade: str
    id_partido: str
    sigla_partido: str
    sigla_uf: str
    praca: str
    website: str
    facebook: str
    instagram: str
    twitter: str
    url_foto: str
    condicao_eleitoral: str
    is_active: bool
    situacao: str
    gabinete: str
    email: str

    def __post_init__(self):
        if isinstance(self.gabinete, str):
            gd = json.loads(self.gabinete)
            for k, v in gd.items():
                if v == "None":
                    gd[k] = None
            self.gabinete = gd

    def compare(self, other):
        diff = []
        sdict = self.__dict__
        odict = other.__dict__
        for k in sdict.keys():
            if sdict[k] != odict[k]:
                diff.append(k)
        return diff


@dataclass
class Discurso:
    "Representation of a speech."
    id_parl: str
    data_hora_inicio: datetime
    sigla_tipo_discurso: str
    tipo_descricao: str
    keywords: str
    sumario: str
    tipo: str
    data_hora_fim: str | None = None
    transcricao: str | None = None
    url_evento: str | None = None
    url_audio: str | None = None
    url_texto: str | None = None
    url_video: str | None = None
    praca: str | None = None
    id: int | None = None
    related_proj_name: str | None = None

    def __post_init__(self):
        if isinstance(self.data_hora_inicio, str):
            self.data_hora_inicio = datetime.strptime(
                self.data_hora_inicio, "%Y-%m-%dT%H:%M:%S"
            )


@dataclass
class Reputacao:
    "Representation of reputation info."
    id_parl: str
    cargo: str
    nome: str
    profissao: str
    mandato: str
    n_vezes_cabeca: int
    debatedor: str
    articulador_organizador: str
    formulador: str
    formador: str
    negociador: str
    cod_perfil: int
    ano: int


@dataclass
class Lideranca:
    id_parl: str
    tipo_unidade_lideranca: str
    cod_unidade: str
    sigla_unidade: str
    nome_unidade: str
    praca: str
    descricao_tipo_lideranca: str
    data_inicio: datetime
    data_fim: datetime
    peso: int
    is_active: bool


@dataclass
class Profissao:
    cod: str
    nome: str
    sigla: str = ""
    descricao: str = ""


@dataclass
class ParlamentarProfissao:
    id_parl: str
    titulo: str
    cod_tipo_profissao: str
    praca: str
    data_hora: str = field(default_factory=datetime.now)  # type: ignore
