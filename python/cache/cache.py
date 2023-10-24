import sqlite3


def migration():
    con = sqlite3.connect("cache.db")
    cur = con.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS custos (produtocodigo TEXT, datavenda TEXT, custounitario TEXT, lojacodigo TEXT)')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS produtos (produtocodigo TEXT, lojacodigo TEXT, grupoprodutocodigo TEXT, grupoprodutonome TEXT, subgrupoprodutocodigo TEXT, subgrupoprodutonome TEXT, fornecedorcodigo TEXT, fornecedornome TEXT)')

    con.commit()
    con.close()


def upsertCost(produtocodigo: str, lojacodigo: str, datavenda: str, custounitario: str):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM custos WHERE produtocodigo = ? and lojacodigo = ?", (produtocodigo, lojacodigo))
    existente = cursor.fetchone()

    if existente:

        cursor.execute(
            "UPDATE custos SET datavenda = ?, custounitario = ? WHERE produtocodigo = ? and lojacodigo = ?", (datavenda, custounitario, produtocodigo, lojacodigo))
    else:

        cursor.execute(
            "INSERT INTO custos (produtocodigo, datavenda, custounitario, lojacodigo) VALUES (?, ?, ?, ?)",
            (produtocodigo, datavenda, custounitario, lojacodigo))

    cursor.execute("SELECT count(*) FROM custos")
    total = cursor.fetchall()

    print('🚀 ~ total de linhas nos custos:', total)

    conn.commit()
    conn.close()


def findOneCost(produtocodigo: str, lojacodigo: str):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM custos WHERE produtocodigo = ? and lojacodigo = ?", (produtocodigo, lojacodigo))

    custo = cursor.fetchone()

    if custo:
        column_names = [desc[0] for desc in cursor.description]
        custo_dict = dict(zip(column_names, custo))

        conn.commit()
        conn.close()

        return custo_dict
    else:
        return None


def upsertProduct(produtocodigo: str, lojacodigo: str, grupoprodutocodigo: str, grupoprodutonome: str, subgrupoprodutocodigo: str, subgrupoprodutonome: str, fornecedorcodigo: str, fornecedornome: str):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM produtos WHERE produtocodigo = ? and lojacodigo = ?", (produtocodigo, lojacodigo))
    existente = cursor.fetchone()

    if existente:
        cursor.execute(
            "UPDATE produtos SET grupoprodutocodigo = ?, grupoprodutonome = ?, subgrupoprodutocodigo = ?, subgrupoprodutonome = ?, fornecedorcodigo = ?, fornecedornome = ? WHERE produtocodigo = ? and lojacodigo = ?",
            (grupoprodutocodigo, grupoprodutonome, subgrupoprodutocodigo, subgrupoprodutonome, fornecedorcodigo, fornecedornome, produtocodigo, lojacodigo))
    else:

        cursor.execute(
            "INSERT INTO produtos (produtocodigo, lojacodigo, grupoprodutocodigo, grupoprodutonome, subgrupoprodutocodigo, subgrupoprodutonome, fornecedorcodigo, fornecedornome) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (produtocodigo, lojacodigo, grupoprodutocodigo, grupoprodutonome, subgrupoprodutocodigo, subgrupoprodutonome, fornecedorcodigo, fornecedornome))

    cursor.execute("SELECT count(*) FROM produtos")
    total = cursor.fetchall()

    print('🚀 ~ total de linhas nos produtos:', total)

    conn.commit()
    conn.close()


def findOneProduct(produtocodigo: str, lojacodigo: str):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM produtos WHERE produtocodigo = ? and lojacodigo = ?", (produtocodigo, lojacodigo))

    produto = cursor.fetchone()

    if produto:
        column_names = [desc[0] for desc in cursor.description]
        produto_dict = dict(zip(column_names, produto))

        conn.commit()
        conn.close()

        return produto_dict
    else:
        return None
