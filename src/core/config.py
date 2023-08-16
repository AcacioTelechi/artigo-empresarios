from dataclasses import dataclass, field
from time import sleep

import requests
from .utils import add_url_path, add_url_params


URL_BASE = "https://dadosabertos.camara.leg.br/api/v2/"


@dataclass
class Config():
    endpoint: str
    parameters: dict = field(default_factory=dict)
    file_name: str = field(default_factory=str)

    def __post_init__(self):
        url_endpoint = add_url_path(URL_BASE, self.endpoint)
        self.url = add_url_params(url_endpoint, self.parameters)


def get_data(url: str) -> list[dict]:
    arqv = []
    while True:
        try:
            response = requests.get(url)
        except TimeoutError or requests.exceptions.ConnectTimeout or requests.exceptions.Timeout:
            print("Timeout: sleeping for 60 secs")
            sleep(60)
            continue
        except requests.exceptions.ConnectionError:
            print("ConnectionError: sleeping for 60 secs")
            sleep(60)
            continue
        if response.status_code == 200:
            resp = response.json()
            if isinstance(resp["dados"], list):
                arqv += resp["dados"]
            else:
                arqv.append(resp["dados"])
            rels = [link["rel"] for link in resp["links"]]
            if "next" in rels:
                url = resp["links"][rels.index("next")]["href"]
            else:
                break
        elif response.status_code == 502:
            print('ERRO 502, sleeping for 5 minutes')
            sleep(300)
        else:
            print('URL: ', url)
            raise ConnectionError(response.status_code)
    return arqv
