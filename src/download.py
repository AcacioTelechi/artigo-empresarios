import os
from typing import List
from datetime import datetime

import pandas as pd
from tqdm import tqdm

from .core import (
    ArvoreApensados,
    Config,
    Node,
    Parlamentar,
    ParlamentarProfissao,
    Proposicao,
    ProposicaoAutor,
    ProposicaoDetalhes,
    Votacao,
    Voto,
    OrientacaoVoto,
    get_data,
)


def get_parlamentares(
    parameters: dict = {"dataInicio": "2018-01-01", "dataFim": "2023-01-01"}
):
    config = Config(
        endpoint="deputados",
        parameters=parameters,
    )
    data = get_data(config.url)

    parls = [
        Parlamentar(
            id_parl=d["id"],
            nome=d["nome"],
            sigla_partido=d["siglaPartido"],
            sigla_uf=d["siglaUf"],
            is_active=True,
            praca="cd",
        )
        for d in data
    ]
    return parls


def get_profissoes(parlamentares: List[Parlamentar]) -> List[ParlamentarProfissao]:
    final = []
    for parl in tqdm(parlamentares, "Detalhes dos Parlamentares"):
        config_prof = Config(
            endpoint=f"deputados/{parl.id_parl}/profissoes", file_name=parl.id_parl
        )
        resp = get_data(config_prof.url)
        if len(resp) == 0:
            continue
        final.append(
            ParlamentarProfissao(
                id_parl=parl.id_parl,
                titulo=resp[0]["titulo"],
                cod_tipo_profissao=resp[0]["codTipoProfissao"],
                praca="cd",
            )
        )
    return final


def get_arvore_apensados(list_props: List[Proposicao]) -> ArvoreApensados:
    def find_related_projs(prop: Proposicao):
        config = Config(endpoint=f"proposicoes/{prop.id_prop}/relacionadas")
        resp = get_data(config.url)

        proposicoes_relacionadas = []
        for item in resp:
            url_detalhes = item["uri"]
            detalhes = get_data(url_detalhes)[0]
            proposicoes_relacionadas.append(
                Proposicao(
                    id_prop=str(detalhes["id"]),
                    sigla_tipo=detalhes["siglaTipo"],
                    ano=detalhes["ano"],
                    ementa=detalhes["ementa"],
                    numero=detalhes["numero"],
                    is_prl=detalhes["siglaTipo"] == "PRL",
                    praca="cd",
                    data_apresentacao=datetime.strptime(
                        detalhes["dataApresentacao"], "%Y-%m-%dT%H:%M"
                    ),
                )
            )

        return proposicoes_relacionadas

    # percorrer árvore de apensados
    def montar_arvore(props_ref: list[Proposicao], p_bar: tqdm):
        final = []
        for prop in props_ref:
            resp = find_related_projs(prop)
            node = Node(prop, resp)
            if len(resp) > 0:
                p_bar.total += len(resp)
                p_bar.refresh()
                children = montar_arvore(resp, p_bar)
                node.children = children
            p_bar.update(1)
            final.append(node)
        return final

    pbar = tqdm(list_props, desc="Árvore de Apensados\t")
    arvore = montar_arvore(list_props, pbar)
    pbar.close()
    return ArvoreApensados(arvore)


def get_projects_by_name(proposicoes: List[Proposicao]) -> List[Proposicao]:
    "Find projects by name."
    # encontrar ids dos projetos
    for proposicao in proposicoes:
        config = Config(
            endpoint="proposicoes",
            parameters={
                "siglaTipo": proposicao.sigla_tipo,
                "numero": proposicao.numero,
                "ano": proposicao.ano,
            },
        )
        data = get_data(config.url)
        if len(data) > 0:
            proposicao.id_prop = str(data[0]["id"])
        else:
            print(
                f"{proposicao.sigla_tipo} {proposicao.numero}/{proposicao.ano} não encontrado\n URL: {config.url}"
            )
    return proposicoes


def get_autores(list_projs: List[Proposicao]) -> List[ProposicaoAutor]:
    # pegar autores
    autores_relacionadas = []
    for proj in tqdm(list_projs, desc="Autores"):
        config = Config(endpoint=f"proposicoes/{proj.id_prop}/autores")
        autores = get_data(config.url)
        resp = []
        for autor in autores:
            autor_obj = ProposicaoAutor(
                id_prop=str(proj.id_prop),
                id_autor=autor["uri"].split("/")[-1],
                tipo_autor=autor["tipo"],
                ordem_assinatura=autor["ordemAssinatura"],
                proponente=autor["proponente"] == 1,
                praca="cd",
            )
            resp.append(autor_obj)
        autores_relacionadas += resp
    return autores_relacionadas


def get_proposicoes_detalhes(
    proposicoes: list[Proposicao],
) -> list[ProposicaoDetalhes]:
    objs = []

    for proposicao in tqdm(proposicoes, desc="Baixando Proposições"):
        config = Config(endpoint=f"proposicoes/{proposicao.id_prop}")
        resp = get_data(config.url)[0]
        obj = ProposicaoDetalhes(
            id_prop=str(resp["id"]),
            sigla_tipo=resp["siglaTipo"],
            numero=resp["numero"],
            ano=resp["ano"],
            is_prl=True if resp["siglaTipo"] == "PRL" else False,
            praca="cd",
            data_apresentacao=resp["dataApresentacao"],
            ementa=resp["ementa"],
            cod_tipo=resp["codTipo"],
            tipo_descr=resp["descricaoTipo"],
            ementa_detalhada=resp["ementaDetalhada"],
            keywords=resp["keywords"],
            url_inteiro_teor=resp["urlInteiroTeor"],
            uri=resp["uri"],
            texto=resp["texto"],
            justificativa=resp["justificativa"],
            status_data=resp["statusProposicao"]["dataHora"],
            status_sequencia=resp["statusProposicao"]["sequencia"],
            status_sigla_orgao=resp["statusProposicao"]["siglaOrgao"],
            status_regime=resp["statusProposicao"]["regime"],
            status_descr_situacao=resp["statusProposicao"]["descricaoSituacao"],
            status_cod_tipo_situacao=resp["statusProposicao"]["codTipoTramitacao"],
            status_cod_situacao=resp["statusProposicao"]["codSituacao"],
            status_despacho=resp["statusProposicao"]["despacho"],
            url=resp["statusProposicao"]["url"],
            status_ambito=resp["statusProposicao"]["ambito"],
            status_apreciacao=resp["statusProposicao"]["apreciacao"],
            is_tramit=None,  # type: ignore
            status_id_org=resp["statusProposicao"]["uriOrgao"].split("/")[-1],
        )

        objs.append(obj)

    return objs


def get_votacoes(list_props: List[Proposicao]) -> List[Votacao]:
    """get votacoes por proposicao"""
    votacoes = []
    id_proposicoes_com_votacoes = []
    for prop in tqdm(list_props, desc="Votações"):
        config = Config(endpoint=f"proposicoes/{prop.id_prop}/votacoes")
        resp = get_data(config.url)
        if len(resp) == 0:
            continue
        id_proposicoes_com_votacoes.append(prop.id_prop)
        for vot in resp:
            votacoes.append(
                Votacao(
                    praca="cd",
                    id_votacao=vot["id"],
                    id_prop=prop.id_prop,
                    data_hora_registro=vot["dataHoraRegistro"],
                    sigla_orgao=vot["siglaOrgao"],
                    descricao=vot["descricao"],
                    aprovacao=vot["aprovacao"] == 1,
                )
            )
    # get detalhes das votações
    for votacao in tqdm(votacoes, desc="Detalhes Votações"):
        config = Config(endpoint=f"votacoes/{votacao.id_votacao}")
        resp = get_data(config.url)[0]
        votacao.uriProposicaoCitada = resp["ultimaApresentacaoProposicao"][
            "uriProposicaoCitada"
        ]
        votacao.ultimaApresentacaoProposicaoDescricao = resp[
            "ultimaApresentacaoProposicao"
        ]["descricao"]
    print(
        f"{len(votacoes)} votações em {len(id_proposicoes_com_votacoes)} proposições."
    )
    return votacoes


def get_votos(votacoes: List[Votacao]):
    id_votacoes_com_votos = []
    votos = []
    for votacao in tqdm(votacoes, "Votacoes analisadas"):
        config = Config(endpoint=f"votacoes/{votacao.id_votacao}/votos")
        resp = get_data(config.url)
        if len(resp) == 0:
            continue
        for vot in resp:
            votos.append(
                Voto(
                    praca="cd",
                    voto=vot["tipoVoto"],
                    id_parl=str(vot["deputado_"]["id"]),
                    sigla_partido=vot["deputado_"]["siglaPartido"],
                    id_votacao=votacao.id_votacao,
                )
            )
        id_votacoes_com_votos.append(votacao.id_votacao)
    print(f"{len(votos)} votos em {len(id_votacoes_com_votos)} votações.")
    return votos

def get_orientacoes(votacoes: List[Votacao]):
    orientacoes = []
    for votacao in tqdm(votacoes, "Buscando Orientações"):
        config = Config(endpoint=f"votacoes/{votacao.id_votacao}/orientacoes")
        resp = get_data(config.url)
        if len(resp) == 0:
            continue
        for ori in resp:
            orientacoes.append(
                OrientacaoVoto(
                    cod_partido_bloco=ori['codPartidoBloco'],
                    cod_tipo_lideranca=ori['codTipoLideranca'],
                    orientacao_voto=ori['orientacaoVoto'],
                    sigla_partido_bloco=ori['siglaPartidoBloco'],
                    id_votacao=votacao.id_votacao,
                )
            )
    return orientacoes

def main():
    # parls = get_parlamentares()
    # profs = get_profissoes(parls)

    # pd.DataFrame(parls).to_csv("./data/parlamentares.csv", index=False)
    # pd.DataFrame(profs).to_csv("./data/profissoes.csv", index=False)

    projs = pd.read_excel(r"./projetos_selecionados.xlsx")
    for idx in projs.index:
        prop = Proposicao(
            sigla_tipo=projs.loc[idx, "tipo"],  # type: ignore
            numero=projs.loc[idx, "código"],  # type: ignore
            ano=projs.loc[idx, "ano "],  # type: ignore
        )

        resp = get_projects_by_name([prop])

        arvore = get_arvore_apensados(resp)

        autores = get_autores(arvore.nodes)

        props_detalhes = get_proposicoes_detalhes(arvore.nodes)

        votacoes = get_votacoes(arvore.nodes)

        votos = get_votos(votacoes)

        nome_tema = projs.loc[idx, "tema "]

        path = f"./data/{nome_tema}"
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        pd.DataFrame(props_detalhes).to_csv(path + "/projetos.csv", index=False)
        pd.DataFrame(autores).to_csv(path + "/autores.csv", index=False)
        pd.DataFrame(votacoes).to_csv(path + "/votacoes.csv", index=False)
        pd.DataFrame(votos).to_csv(path + "/votos.csv", index=False)


if __name__ == "__main__":
    main()
