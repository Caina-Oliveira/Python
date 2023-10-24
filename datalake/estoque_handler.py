import contextlib
import requests
import json
from datetime import datetime
from log.log import log_cs
from cache import cache


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


def get_balances(token: str, module: str):
    url = "https://apitotvsmoda.bhan.com.br"

    headers_sell = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}"
    }

    data_atual = datetime.now().strftime("%Y-%m-%d")
    branch_codes = [6, 7, 9, 13]  # Lista de lojas a serem pesquisadas
    for branch_code in branch_codes:
        log_cs(f'Buscando estoque loja {branch_code}')
        count = 1

        while True:
            estoque = []
            payload_sell = {
                "filter": {
                    "change": {
                        "startDate": "2020-01-02T00:00:19.056Z",
                        "endDate": data_atual,
                        "inStock": True,
                        "branchStockCodeList": [6],
                        "stockCodeList": [1]
                    },
                    "hasStock": True,
                    "branchStockCode": branch_code,
                    "stockCode": 1
                    # ,"productCodeList": [107544, 107542, 102631]
                },
                "option": {
                    "balances": [
                        {
                            "branchCode": branch_code,
                            "stockCodeList": [1]
                        }
                    ]
                },
                "page": count,
                "expand": "items"
            }

            response_sell = requests.post(
                f'{url}/api/totvsmoda/product/v2/balances/search', json=payload_sell, headers=headers_sell).json()

            with contextlib.suppress(TypeError):
                for item in response_sell['items']:
                    tmp_item = {
                        "lojacodigo": item['balances'][0]['branchCode'],
                        "localcodigo": item['balances'][0]['stockCode'],
                        "localnome": item['balances'][0]['stockDescription'],
                        "produtocodigo": str(item['productCode']),
                        "produtonome": item['productName'],
                        "quantidade": item['balances'][0]['stock'],
                        "datareferencia": datetime.strftime(datetime.strptime(data_atual, '%Y-%m-%d'), '%d/%m/%Y 00:00:00'),
                        "status": "A",
                        "data": datetime.strftime(datetime.strptime(data_atual, '%Y-%m-%d'), '%Y%m%d'),
                        "FilterDate": item['maxChangeFilterDate']
                    }

                    estoque.append(tmp_item)

            with open(f'tmp/{module}/estoque.{branch_code}.{count}.json', 'w') as f:
                json.dump({"data": estoque}, f, indent=4)
            if response_sell['hasNext'] == False:
                log_cs(f'Finalizando estoque loja {branch_code}')
                break

            count += 1


def get_products_cost(invoice_date: str, produtocodigo: int, lojacodigo: int, token: str):
    log_cs(f"Buscando Custos para produto: {produtocodigo} loja: {lojacodigo}")

    custo = cache.findOneCost(
        produtocodigo=produtocodigo, lojacodigo=lojacodigo)

    if custo:
        log_cs(
            f"Pegou Custo do cache produtocodigo: {produtocodigo} loja: {lojacodigo}")
        return {
            "produtocodigo": produtocodigo,
            "lojacodigo": lojacodigo,
            "datavenda": datetime.strftime(datetime.strptime(invoice_date, '%Y-%m-%dT%H:%M:%S.%fZ'), '%d/%m/%Y %H:%M:%S'),
            "custounitario": float(custo['custounitario']),
        }

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

    response_sell = requests.post(
        f'{url}/api/totvsmoda/product/v2/costs/search', json=payload_sell, headers=headers_sell).json()

    tmp_product = {}

    for products in response_sell['items']:

        tmp_product = {
            "produtocodigo": produtocodigo,
            "lojacodigo": lojacodigo,
            "datavenda": datetime.strftime(datetime.strptime(invoice_date, '%Y-%m-%dT%H:%M:%S.%fZ'), '%d/%m/%Y %H:%M:%S'),
        }

        for costs in products['costs']:
            tmp_product_valor = {
                "custounitario": costs['cost']
            }
            tmp_product = {**tmp_product, **tmp_product_valor}
            # product.append(tmp_product)

    if tmp_product.get('produtocodigo') is not None:
        cache.upsertCost(produtocodigo=tmp_product['produtocodigo'], lojacodigo=tmp_product['lojacodigo'],
                         custounitario=str(tmp_product['custounitario']), datavenda=tmp_product['datavenda'])
    else:
        log_cs(f"Não veio custo do produto {produtocodigo}")

    return tmp_product


def get_products_category(produtocodigo: int, lojacodigo: int, token: str):
    log_cs(f"Buscando Categoria para : {produtocodigo} loja: {lojacodigo}")

    produto = cache.findOneProduct(
        produtocodigo=produtocodigo, lojacodigo=lojacodigo)

    if produto:
        log_cs(
            f"Pegou Produto do cache produtocodigo: {produtocodigo} loja: {lojacodigo}")

        return {
            "produtocodigo": str(produtocodigo),
            "lojacodigo": lojacodigo,
            "grupoprodutocodigo": produto['grupoprodutocodigo'],
            "grupoprodutonome": produto['grupoprodutonome'],
            "subgrupoprodutocodigo": produto['subgrupoprodutocodigo'],
            "subgrupoprodutonome": produto['subgrupoprodutonome'],
            "fornecedorcodigo": produto['fornecedorcodigo'],
            "fornecedornome": produto['fornecedornome'],
        }

    url = "https://apitotvsmoda.bhan.com.br"

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
    response_sell = requests.post(
        f'{url}/api/totvsmoda/product/v2/references/search', json=payload_sell, headers=headers_sell).json()

    # print('🚀 ~ response_sell:', response_sell)

    tmp_mercadologico = {
        "produtocodigo": str(produtocodigo),
        "lojacodigo": lojacodigo,
        "grupoprodutocodigo": None,
        "grupoprodutonome": None,
        "subgrupoprodutocodigo": None,
        "subgrupoprodutonome": None,
        "fornecedorcodigo": None,
        "fornecedornome": None,
    }

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

    cache.upsertProduct(produtocodigo=tmp_mercadologico["produtocodigo"],
                        lojacodigo=tmp_mercadologico["lojacodigo"],
                        fornecedorcodigo=tmp_mercadologico["fornecedorcodigo"],
                        fornecedornome=tmp_mercadologico["fornecedornome"],
                        grupoprodutocodigo=tmp_mercadologico["grupoprodutocodigo"],
                        grupoprodutonome=tmp_mercadologico["grupoprodutonome"],
                        subgrupoprodutocodigo=tmp_mercadologico["subgrupoprodutocodigo"],
                        subgrupoprodutonome=tmp_mercadologico["subgrupoprodutonome"])

    return tmp_mercadologico
