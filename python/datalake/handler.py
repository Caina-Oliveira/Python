import contextlib
import requests
import functools
import json
from datetime import datetime, timedelta
from pytz import timezone
from log.log import log_cs


def get_last_time_update() -> list:
    try:

        with open('python/configurations/time.json', 'r') as f:
            time = json.load(f)

    except FileNotFoundError:

        time = datetime.now(
            timezone('America/Sao_Paulo')) - timedelta(days=2*365)
        time = datetime(time.year, 1, 1)

        time = datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%fZ")

        time = time[:-4] + "{:02d}Z".format(int(time[-4:-2]))

        time = {
            "time": time}

        with open('python/configurations/time.json', 'w') as f:
            json.dump(time, f)
            # time = json.load(f)

    date_update = datetime.now(
        timezone('America/Sao_Paulo')).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    date_update = date_update[:-4] + "{:02d}Z".format(int(date_update[-4:-2]))

    with open('python/configurations/time.json', 'w') as f:
        json.dump({"time": date_update}, f)

    return [time['time'], date_update]


def get_token():
    url = "https://apitotvsmoda.bhan.com.br"
    headers_auth = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {
        "client_id": "jolieapiv2",
        "client_secret": "2754411239",
        "grant_type": "password",
        "username": "IZIAPP",
        "password": "2023"
    }
    response = requests.post(
        f'{url}/api/totvsmoda/authorization/v2/token', data=payload, headers=headers_auth)
    token = response.json()['access_token']
    log_cs(token)
    return token


def get_sales(token: str, date_start: str, date_end: str, module: str):
    url = "https://apitotvsmoda.bhan.com.br"

    headers_sell = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}"
    }
    count = 1

    while True:
        vendaitem = []
        payload_sell = {
            "filter": {
                "startIssueDate": date_start,
                "endIssueDate": date_end,
                "branchCodeList": [
                    6, 7, 9, 13
                ],
                "invoiceStatusList": [
                    "Canceled", "Normal", "Deleted", "Issued", "Denied"
                ],
                "eletronicInvoiceStatusList": [
                    "Authorized", "Sent", "Generated"
                ]
            },
            "page": count,
            "expand": "items"
        }

        response_sell = requests.post(f'{url}/api/totvsmoda/fiscal/v2/invoices/search',
                                      json=payload_sell, headers=headers_sell).json()
        with contextlib.suppress(TypeError):
            for invoice in response_sell['items']:
                if invoice['operationCode'] in {
                    1702,
                    1501,
                    1300,
                    1306,
                    1603,
                    1233,
                    1534,
                    1570,
                    1222,
                    1524,
                    1009,
                    1301,
                    1001,
                } and {x['cfop'] for x in invoice['items']} <= {
                    1410,
                    1411,
                    2201,
                    2202,
                    2410,
                    5101,
                    5102,
                    5403,
                    6101,
                    6102,
                    6107,
                    6108,
                }:
                    tmp_vendaitem = {
                        "vendacodigo": invoice['invoiceSequence'],
                        "lojacodigo": invoice['branchCode'],
                        # "lojanome": invoice[''],
                        "datavenda": datetime.strftime(datetime.strptime(invoice['invoiceDate'], '%Y-%m-%d'), '%d/%m/%Y') + ' 00:00:00',
                        "data": datetime.strftime(datetime.strptime(invoice['invoiceDate'], '%Y-%m-%d'), '%Y%m%d'),
                        "anovenda": datetime.strftime(datetime.strptime(invoice['invoiceDate'], '%Y-%m-%d'), '%Y'),
                        "mesvenda": datetime.strftime(datetime.strptime(invoice['invoiceDate'], '%Y-%m-%d'), '%m'),
                        "diavenda": datetime.strftime(datetime.strptime(invoice['invoiceDate'], '%Y-%m-%d'), '%d'),
                        "agrupadorhoravenda": invoice['exitTime'].split(':')[0],
                        "situacaovenda": "Normal" if invoice['invoiceStatus'] == "Issued" else invoice['invoiceStatus'],
                        # "tipo": invoice['invoiceStatus'],
                        "totalvenda": invoice['totalValue'],
                        "clientecodigo": invoice['personCode'],
                        "clientenome": invoice['personName'],
                    }

                    for items in invoice['items']:

                        item = {
                            "produtocodigo": items['code'],
                            "produtonome": items['name'],
                            "quantidade": -1 * items['quantity'] if items['cfop'] in [1410, 1411, 2201, 2202, 2410] else items['quantity'],
                            "vendedorcodigo": items['products'][0]['dealerCode'],
                            "cfop": items['cfop'],
                            "valorliquidoitem": -1 * items['unitNetValue'] * items['quantity'] if items['cfop'] in [1410, 1411, 2201, 2202, 2410] else items['quantity'] * items['unitNetValue']
                        }
                        vendaitem.append(tmp_vendaitem | item)
        with open(f'tmp/{module}/vendas.1.{count}.json', 'w') as f:
            json.dump({"data": vendaitem}, f, indent=4)
        if response_sell['hasNext'] == False:
            break

        count += 1


def get_products_cost(invoice_date: str, produtocodigo: int, lojacodigo: int, token: str):
    log_cs(f"Buscando Custos para : {produtocodigo}")
    url = "https://apitotvsmoda.bhan.com.br"
    headers_sell = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}"
    }

    payload_sell = {
        "filter": {
            "change": {
                "startDate": "1900-01-01T00:00:00.00000Z",
                "endDate": invoice_date,
                # "startDate": "2023-03-01T00:00:00.000Z",
                # "endDate": "2023-03-10T00:00:00.000Z",
                "inCost": True,
                "branchCostCodeList": [
                    1, 6, 7, 9, 13

                ],
                # "endProductCode": [104240],
                "costCodeList": [9]
            },
            "productCodeList": [produtocodigo],
        },

        "option": {
            "costs": [
                {
                    "branchCode": lojacodigo,
                    "costCodeList": [
                        9
                    ]
                }
            ]
        }}

    response_sell = requests.post(f'{url}/api/totvsmoda/product/v2/costs/search',
                                  json=payload_sell, headers=headers_sell).json()
    for products in response_sell['items']:

        tmp_product = {
            "produtocodigo": str(products['productCode']),
            "datavenda": datetime.strftime(datetime.strptime(invoice_date, '%Y-%m-%dT%H:%M:%S.%fZ'), '%d/%m/%Y %H:%M:%S'),

        }
        for costs in products['costs']:
            tmp_product_valor = {
                "custounitario": costs['cost'],
                "lojacodigo": costs['branchCode'],
            }
            tmp_product = {**tmp_product, **tmp_product_valor}
            # product.append(tmp_product)

    return tmp_product


def get_products_category(produtocodigo: int, lojacodigo: int, token: str):

    url = "https://apitotvsmoda.bhan.com.br"

    log_cs(f"Buscando Categoria para : {produtocodigo}")
    headers_sell = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}"
    }

    payload_sell = {
        "filter": {
            "productCodeList": [produtocodigo],
        },

        "option": {

            "branchInfoCode": lojacodigo,

        },
        "expand": "classifications,suppliers"

    }
    response_sell = requests.post(f'{url}/api/totvsmoda/product/v2/references/search',
                                  json=payload_sell, headers=headers_sell).json()
    tmp_mercadologico = {"produtocodigo": str(produtocodigo),
                         "lojacodigo": lojacodigo,
                         "grupoprodutocodigo": None,
                         "grupoprodutonome": None,
                         "subgrupoprodutocodigo": None,
                         "subgrupoprodutonome": None,
                         "fornecedorcodigo": None,
                         "fornecedornome": None, }
    for arvore in response_sell['items'][0]['colors'][0]['products'][0]['classifications']:
        if arvore['typeCode'] == 118:
            tmp_mercadologico.update({
                "grupoprodutocodigo": arvore['name'],
                "grupoprodutonome": arvore['name'],
            })
        elif arvore['typeCode'] == 101:
            tmp_mercadologico.update({
                "subgrupoprodutocodigo": arvore['name'],
                "subgrupoprodutonome": arvore['name'],
            })
    for suplies in response_sell['items'][0]['colors'][0]['products'][0]['suppliers']:
        tmp_mercadologico.update({
            "fornecedorcodigo": str(suplies['code']),
            "fornecedornome": suplies['name'],
        })

    return tmp_mercadologico


@functools.lru_cache(maxsize=None)
def get_vendedor(vendedorcodigo: int, lojacodigo: int, token: str):
    log_cs(f"Buscando Vendedor para : {vendedorcodigo}")

    if get_vendedor.cache_info().currsize > 0:
        log_cs("Buscando do cache.")
    else:
        log_cs("Fazendo chamada à API.")

    url = "https://apitotvsmoda.bhan.com.br"
    headers_sell = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}"
    }

    payload_sell = {
        "filter": {
            "sellerCode": vendedorcodigo
        },
        "branchCodeList": [
            6, 7, 9, 13
        ]
    }
    response_sell = requests.post(f'{url}/api/totvsmoda/seller/v2/search',
                                  json=payload_sell, headers=headers_sell).json()
    for vendedor in response_sell['items']:
        tmp_vendedor = {"vendedorcodigo": str(vendedorcodigo),
                        "lojacodigo": lojacodigo,
                        "vendedornome": vendedor['sellerName']
                        }
    return tmp_vendedor
