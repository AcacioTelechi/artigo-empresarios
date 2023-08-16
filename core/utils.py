import datetime
import datetime
import json
from urllib.parse import (ParseResult, parse_qsl, unquote, urlencode, urljoin,
                          urlparse)

import unidecode


def add_url_params(url:str, params: dict) -> str:
    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL
    
    >> url = 'https://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'https://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't lose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    # Bool and Dict values should be converted to json-friendly values
    parsed_get_args.update(
        {k: json.dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url

def add_url_path(url:str, path: dict) -> str:
    return urljoin(url, path)


def trat_str(string: str) -> str:
    return unidecode.unidecode(str(string)).lower()

def trat_cpf(cpf) -> str:
    cpf_str = str(cpf)
    return cpf_str.rjust(11, '0')

def trat_tit_eleitoral(tit) -> str:
    tit_str = str(tit)
    return tit_str.rjust(12, '0')

def infinite_date_generator(date: datetime):
    while True:
        yield date
        date += datetime.timedelta(1)

def infinite_date_generator(date: datetime):
    while True:
        yield date
        date += datetime.timedelta(1)


def transform_datetime_format(datetime_string: str) -> datetime.datetime:
    formats = [
        '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S', '%Y/%m/%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M', '%Y/%m/%dT%H:%M',
        '%d-%b-%y %I:%M:%S %p', '%d-%b-%Y %I:%M:%S %p',
        '%d/%m/%y %I:%M:%S %p', '%d/%m/%Y %I:%M:%S %p',
        '%m/%d/%y %I:%M:%S %p', '%m/%d/%Y %I:%M:%S %p',
        '%d-%m-%y %I:%M:%S %p', '%d-%m-%Y %I:%M:%S %p',
        '%d.%m.%y %I:%M:%S %p', '%d.%m.%Y %I:%M:%S %p',
        '%d %b %y %I:%M:%S %p', '%d %b %Y %I:%M:%S %p',
        '%d-%b-%y %I:%M %p', '%d-%b-%Y %I:%M %p',
        '%d/%m/%y %I:%M %p', '%d/%m/%Y %I:%M %p',
        '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
        '%m/%d/%y %I:%M %p', '%m/%d/%Y %I:%M %p',
        '%d-%m-%y %I:%M %p', '%d-%m-%Y %I:%M %p',
        '%d.%m.%y %I:%M %p', '%d.%m.%Y %I:%M %p',
        '%d %b %y %I:%M %p', '%d %b %Y %I:%M %p',
    ]

    for format in formats:
        try:
            datetime_obj = datetime.datetime.strptime(datetime_string, format)
            return datetime_obj
        except ValueError:
            pass

    raise ValueError(f'Datetime {datetime_string} not configured.')
