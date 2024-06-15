import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib


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


def listar_usuarios():
    conexao = conectar_localBD()
    if conexao is None:
        return []

    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT * FROM usuarios"
    cursor.execute(sql)
    resultados = cursor.fetchall()
    conexao.close()
    return resultados


def cadastrar_usuario(nome, email, senha, tipo):
    conexao = conectar_localBD()
    cursor = conexao.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    sql = "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (nome, email, senha_hash, tipo))
    conexao.commit()
    cursor.close()
    conexao.close()


def logar_usuario(email, senha):
    conexao = conectar_localBD()
    if conexao is None:
        return None

    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
    cursor.execute(sql, (email, senha))
    usuario = cursor.fetchone()
    conexao.close()
    return usuario


def verificar_usuario_existe(email):
    conexao = conectar_localBD()
    cursor = conexao.cursor()
    sql = "SELECT * FROM usuarios WHERE email=%s"
    cursor.execute(sql, (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()
    return usuario is not None


def deletar_usuario(email):
    conexao = conectar_localBD()
    if conexao is None:
        return

    cursor = conexao.cursor()
    sql = "DELETE FROM usuarios WHERE email = %s"
    cursor.execute(sql, (email,))
    conexao.commit()
    conexao.close()
