import sys
from datalake import handler as handler_dl
from datalake import estoque_handler as estoque
from log.log import log_cs
from cache import cache

import pandas as pd
from datetime import datetime
import json
import os


def get_products_info(module: str, token: str):
    for path in os.listdir(f'tmp/{module}/'):

        with open(os.path.join(f'tmp/{module}/', path), 'r') as f:
            data = pd.DataFrame(json.load(f)["data"])
            data_grouped = data[['lojacodigo', 'data', 'produtocodigo', 'datavenda', 'vendedorcodigo']].drop_duplicates(
                subset=['lojacodigo', 'data', 'produtocodigo', 'datavenda', 'vendedorcodigo'])

            custos = []
            vendedor = []
            mercadologico = []
            for row in data_grouped.itertuples(index=False):
                invoice_date = datetime.strftime(datetime.strptime(
                    row[1], '%Y%m%d'), "%Y-%m-%dT%H:%M:%S.%fZ")

                invoice_date = invoice_date[:-4] + \
                    "{:02d}Z".format(int(invoice_date[-4:-2]))

                custo = handler_dl.get_products_cost(
                    lojacodigo=row[0], invoice_date=invoice_date, produtocodigo=int(row[2]), token=token)
                custos.append(custo)

                tmp_vendedor = handler_dl.get_vendedor(
                    vendedorcodigo=(row[4]), lojacodigo=row[0], token=token)
                vendedor.append(tmp_vendedor)

                tmp_mercadologico = handler_dl.get_products_category(
                    lojacodigo=row[0], produtocodigo=int(row[2]), token=token)
                mercadologico.append(tmp_mercadologico)
        log_cs("Gerando Arquivo : " + os.path.join(f'tmp/{module}/', path))

        arvore = pd.DataFrame(mercadologico)

        custos = pd.DataFrame(custos)

        vendedores = pd.DataFrame(vendedor)
        vendedores['vendedorcodigo'] = vendedores['vendedorcodigo'].astype(int)

        data = data.merge(right=arvore.drop_duplicates(), how='left', on=[
            'produtocodigo', 'lojacodigo'])

        data = data.merge(
            right=custos, how='left', on=['produtocodigo', 'lojacodigo', 'datavenda'])

        data = data.merge(
            right=vendedores.drop_duplicates(), how='left', on=['vendedorcodigo', 'lojacodigo'])

        data['custototal'] = data['custounitario'] * data['quantidade']

        data_dict = {"data": data.to_dict(orient="records")}

        with open(os.path.join(f'tmp/{module}/', path), "w") as f:
            json.dump(data_dict, f)


def get_estoque_info(module: str, token: str):
    for path in os.listdir(f'tmp/{module}/'):
        log_cs(f'Atualizando arquivo {path}')

        with open(os.path.join(f'tmp/{module}/', path), 'r') as f:
            data = pd.DataFrame(json.load(f)["data"])
            data['produtocodigo'] = data['produtocodigo'].astype(int)
            data_grouped = data[['lojacodigo', 'produtocodigo', 'datareferencia', 'data']].drop_duplicates(
                subset=['lojacodigo', 'produtocodigo', 'datareferencia'])

            custos = []
            mercadologico = []
            for row in data_grouped.itertuples(index=False):
                invoice_date = datetime.strftime(datetime.strptime(
                    row[3], '%Y%m%d'), "%Y-%m-%dT%H:%M:%S.%fZ")

                invoice_date = invoice_date[:-4] + \
                    "{:02d}Z".format(int(invoice_date[-4:-2]))

                custo = estoque.get_products_cost(
                    lojacodigo=row[0], invoice_date=invoice_date, produtocodigo=int(row[1]), token=token)
                custos.append(custo)

                tmp_mercadologico = estoque.get_products_category(
                    lojacodigo=row[0], produtocodigo=int(row[1]), token=token)
                mercadologico.append(tmp_mercadologico)
        log_cs("Gerando Arquivo : " + os.path.join(f'tmp/{module}/', path))

        arvore = pd.DataFrame(mercadologico)
        arvore['produtocodigo'] = arvore['produtocodigo'].fillna(0).astype(int)
        arvore['fornecedorcodigo'] = arvore['fornecedorcodigo'].fillna(
            'Sem Cadastro')
        arvore['fornecedornome'] = arvore['fornecedornome'].fillna(
            'Sem Cadastro')
        arvore['produtocodigo'] = arvore['produtocodigo'].astype(int)
        custos = pd.DataFrame(custos)
        custos['produtocodigo'] = custos['produtocodigo'].fillna(0).astype(int)
        custos['produtocodigo'] = custos['produtocodigo'].astype(int)

        data = data.merge(right=arvore.drop_duplicates(), how='left', on=[
            'produtocodigo', 'lojacodigo'])

        data = data.merge(
            right=custos, how='left', on=['produtocodigo', 'lojacodigo'])

        data['custounitario'] = data['custounitario'].fillna(0)
        data['custototal'] = data['custounitario'] * data['quantidade']
        data['produtocodigo'] = data['produtocodigo'].astype(str)

        data_dict = {"data": data.to_dict(orient="records")}

        with open(os.path.join(f'tmp/{module}/', path), "w") as f:
            json.dump(data_dict, f)


def main(date_since: str, date_before: str, module: str):
    log_cs(module)

    if not os.path.isdir(f'tmp/{module}/'):
        os.makedirs(f'tmp/{module}/')

    if module in {'IZICASH', 'IZILIVE'}:
        date_since = datetime.strptime(date_since, '%d/%m/%Y')
        date_before = datetime.strptime(date_before, '%d/%m/%Y')
        token = handler_dl.get_token()
        handler_dl.get_sales(token, datetime.strftime(date_since, "%Y-%m-%dT00:00:00.000Z"),
                             datetime.strftime(date_before, "%Y-%m-%dT00:00:00.000Z"), module)
        get_products_info(module, token)
    elif module in {'ESTOQUE'}:
        token = estoque.get_token()
        estoque.get_balances(token, module)
        get_estoque_info(module, token)


if __name__ == '__main__':
    cache.migration()
    main(sys.argv[1], sys.argv[2], sys.argv[3])
