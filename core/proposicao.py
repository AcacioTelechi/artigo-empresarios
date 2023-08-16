"Representation of projects-related objects."

from dataclasses import dataclass, field
from datetime import datetime
from .utils import transform_datetime_format

@dataclass(kw_only=True)
class Proposicao:
    "Representation of a project."
    id_prop: str = ''
    sigla_tipo: str = ''
    numero: str = ''
    ano: str = ''
    is_prl: bool = False
    praca: str = ''
    data_apresentacao: datetime = None
    ementa: str = ''
    orientacao: int = 0

    def __post_init__(self):
        if isinstance(self.data_apresentacao, str):
            self.data_apresentacao = transform_datetime_format(
                self.data_apresentacao)
    
    @property
    def nome(self):
        return self.sigla_tipo + " " + \
            str(self.numero) + "/" + str(self.ano)
    
    @nome.setter
    def nome(self, renamed):
        return renamed
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Proposicao) and self.id_prop == __value.id_prop
    
    def __hash__(self) -> int:
        return hash(self.id_prop)



@dataclass
class ProposicaoAutor:
    "Representation of a projet author."
    id_prop: str
    id_autor: str
    tipo_autor: str
    ordem_assinatura: int
    proponente: bool
    praca: str

@dataclass(kw_only=True)
class ProposicaoDetalhes(Proposicao):
    """Detailed representation of a project"""
    cod_tipo: int
    tipo_descr: str
    ementa_detalhada: str
    keywords: str
    url_inteiro_teor: str 
    uri: str
    texto: str
    justificativa: str
    status_data: datetime
    status_sequencia: int
    status_sigla_orgao: str
    status_regime: str
    status_descr_situacao: str
    status_cod_tipo_situacao: str
    status_cod_situacao: str
    status_despacho: str
    url: str
    status_ambito: str
    status_apreciacao: str
    is_tramit: str
    status_id_org: str

    def __post_init__(self):
        if isinstance(self.data_apresentacao, str):
            self.data_apresentacao = transform_datetime_format(self.data_apresentacao)
        if isinstance(self.status_data, str):
            self.status_data = transform_datetime_format(self.status_data)
        del self.orientacao


@dataclass
class Node:
    parent: Proposicao
    children: list[Proposicao]


@dataclass
class ArvoreApensados:
    "Representation of an arvore project tree."
    arvore_apensados: list[Node]
    nodes: list[Proposicao] = field(init=False, default_factory=list)
    cod_props: list[str] = field(init=False, default_factory=list)
    graph: dict = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._find_nodes()
        self.montar_graph(self.arvore_apensados)

    def _find_nodes(self):
        def get_nodes(nodes: list[Node]):
            for node in nodes:
                if node.parent.id_prop not in self.cod_props:
                    self.nodes += [node.parent]
                    self.cod_props.append(node.parent.id_prop)
                if len(node.children) > 0:
                    get_nodes(node.children)
            return

        return get_nodes(self.arvore_apensados)

    def get_children_ids(self, node: Node):
        return [child.parent.id_prop for child in node.children]

    def montar_graph(self, nodes: Node):
        for node in nodes:
            self.graph[node.parent.id_prop] = self.get_children_ids(node)
            if len(node.children) > 0:
                self.montar_graph(node.children)

    def find_parent_id_prop(self, child_id_prop: str):
        for node, children in self.graph.items():
            if child_id_prop in children:
                return node
