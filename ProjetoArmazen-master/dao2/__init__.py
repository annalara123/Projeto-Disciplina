import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor


def conectar_localBD():
    try:
        con = psycopg2.connect(
            host="localhost",
            database="projeto_de_rene",
            user="postgres",
            password="12345"
        )
        return con
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def listar_produtos():
    conexao = conectar_localBD()
    if conexao is None:
        return []

    try:
        cursor = conexao.cursor(cursor_factory=RealDictCursor)
        sql = "SELECT * FROM produtos"
        cursor.execute(sql)
        resultados = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        resultados = []
    finally:
        conexao.close()

    return resultados


def cadastrar_produto(nome, marca, validade, preco, quantidade_disponivel, foto_caminho):
    conexao = conectar_localBD()
    if conexao is None:
        return

    cursor = conexao.cursor()
    sql = """
        INSERT INTO produtos (nome, marca, validade, preco, quantidade_disponivel, foto_caminho)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    valores = (nome, marca, validade, preco, quantidade_disponivel, foto_caminho)
    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()


def editar_produto(nome, marca, validade, preco, quantidade_disponivel, foto_caminho):
    conexao = conectar_localBD()
    if conexao is None:
        return

    cursor = conexao.cursor()
    sql = """
        UPDATE produtos
        SET nome = %s, marca = %s, validade = %s, preco = %s, quantidade_disponivel = %s
        WHERE foto_caminho = %s
    """
    valores = (nome, marca, validade, preco, quantidade_disponivel, foto_caminho)
    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()


def atualizar_quantidade_produto(nome_produto, quantidade):
    conexao = conectar_localBD()
    if conexao is None:
        return

    cursor = conexao.cursor()
    sql = "UPDATE produtos SET quantidade_disponivel = quantidade_disponivel - %s WHERE nome = %s"
    cursor.execute(sql, (quantidade, nome_produto))
    conexao.commit()
    conexao.close()


def listar_compras(nome_produto=None):
    conexao = conectar_localBD()
    if conexao is None:
        return pd.DataFrame()

    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    if nome_produto:
        sql = """
            SELECT DATE_TRUNC('month', data) AS mes, SUM(valor) AS total_compras 
            FROM compras 
            WHERE nome = %s
            GROUP BY mes 
            ORDER BY mes
        """
        cursor.execute(sql, (nome_produto,))
    else:
        sql = """
            SELECT DATE_TRUNC('month', data) AS mes, SUM(valor) AS total_compras 
            FROM compras 
            GROUP BY mes 
            ORDER BY mes
        """
        cursor.execute(sql)

    resultados = cursor.fetchall()
    conexao.close()
    return pd.DataFrame(resultados)


def obter_dados_compras(nome_produto):
    conexao = conectar_localBD()
    if conexao is None:
        return pd.DataFrame()

    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT data, valor
        FROM compras
        WHERE nome = %s
        ORDER BY data
    """
    cursor.execute(sql, (nome_produto,))
    resultados = cursor.fetchall()
    conexao.close()
    return pd.DataFrame(resultados)


def buscar_produto_por_nome(nome):
    conexao = conectar_localBD()
    if conexao is None:
        return None

    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT * FROM produtos WHERE nome = %s"
    cursor.execute(sql, (nome,))
    produto = cursor.fetchone()
    conexao.close()
    return produto
