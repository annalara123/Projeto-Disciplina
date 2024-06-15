import os

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from flask import Flask, request, session
from flask import render_template, redirect, url_for
from sklearn.linear_model import LinearRegression
from dao import *
from dao2 import *

app = Flask(__name__)
app.secret_key = "jk2h3kj23hrk2h5"
app.config['UPLOAD_FOLDER'] = 'static/imagens/'


@app.route("/")
def inicio():
    return render_template('login.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = logar_usuario(email, senha)

        if usuario:
            session['email'] = usuario['email']
            session['senha'] = senha
            session['tipo'] = usuario['tipo']
            return redirect(url_for('menu'))
        else:
            texto = 'Login ou senha incorretos'
            return render_template('login.html', aviso=texto)
    else:
        return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo = request.form.get('tipo')

        if not senha:
            texto = 'Senha não pode ser nula!'
            return render_template('cadastro.html', aviso=texto)

        if verificar_usuario_existe(email):
            texto = 'Email já cadastrado!'
            return render_template('cadastro.html', aviso=texto)

        cadastrar_usuario(nome, email, senha, tipo)
        texto = 'Cadastro realizado com sucesso!'
        return render_template('login.html', aviso=texto)
    else:
        return render_template('cadastro.html')


@app.route('/sair')
def logout():
    session.pop('email', None)
    session.pop('senha', None)
    session.pop('tipo', None)
    return redirect(url_for('login'))


@app.route('/menu')
def menu():
    if 'email' in session:
        tipo_usuario = session['tipo']
        if tipo_usuario == 'Admin':
            return render_template('menu_admin.html')
        else:
            return render_template('menu_cliente.html')
    else:
        return redirect(url_for('login'))


@app.route('/meuPerfil')
def perfil():
    if 'email' in session:
        email = session['email']
        senha = session.get('senha', '')
        usuario = logar_usuario(email, senha)
        if usuario:
            return render_template('perfil.html', nome=usuario['nome'], username=email)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/listarProdutos', methods=['GET'])
def listar_produtos_route():
    if 'email' in session:
        produtos = listar_produtos()
        for produto in produtos:
            produto['foto_caminho'] = os.path.join(app.config['UPLOAD_FOLDER'],
                                                   os.path.basename(produto['foto_caminho']))
        return render_template('produtos.html', produtos=produtos)
    else:
        return redirect(url_for('login'))


@app.route('/cadastroProdutos', methods=['GET', 'POST'])
def cadastro_produtos():
    if request.method == 'POST':
        tipo_usuario = session.get('tipo')
        if tipo_usuario != 'Admin':
            return "Acesso negado! Somente usuários do tipo 'Admin' podem cadastrar produtos."

        nome = request.form.get('nome')
        marca = request.form.get('marca')
        validade = request.form.get('validade')
        preco = request.form.get('preco')
        quantidade_disponivel = request.form.get('quantidade_disponivel')
        foto = request.files['foto_caminho']

        foto_caminho = None
        if foto:
            foto_caminho = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_caminho)

        cadastrar_produto(nome, marca, validade, preco, quantidade_disponivel, foto_caminho)
        return 'Produto cadastrado com sucesso!'
    else:
        return render_template('cadastroProdutos.html')


@app.route('/buscarCliente', methods=['GET', 'POST'])
def buscar_cliente():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return "O campo de e-mail está vazio."

        if verificar_usuario_existe(email):
            deletar_usuario(email)
            return "Cliente removido com sucesso!"
        else:
            return "Cliente não encontrado."
    else:
        return render_template('buscar_cliente.html')


@app.route('/pedirProdutos', methods=['GET', 'POST'])
def pedir_produtos():
    if 'email' in session:
        if request.method == 'GET':
            produtos = listar_produtos()
            for produto in produtos:
                produto['foto_caminho'] = os.path.join(app.config['UPLOAD_FOLDER'],
                                                       os.path.basename(produto['foto_caminho']))
            return render_template('pedirProdutos.html', produtos=produtos)
        elif request.method == 'POST':
            produtos = listar_produtos()
            for produto in produtos:
                nome_produto = produto['nome']
                quantidade = request.form.get(f'quantidade_{nome_produto}')
                if quantidade:
                    atualizar_quantidade_produto(nome_produto, int(quantidade))
            return "Pedido realizado com sucesso!"
    else:
        return redirect(url_for('login'))


@app.route("/previsao_compras", methods=['GET'])
def previsao_compras():
    nome_produto = request.args.get('nome_produto')
    dados_compras = listar_compras(nome_produto)

    if dados_compras.empty:
        return "Nenhum dado de compras encontrado."

    print("Dados de compras:")
    print(dados_compras)

    dados_compras['mes'] = pd.to_datetime(dados_compras['mes'])
    dados_compras.set_index('mes', inplace=True)

    y = dados_compras['total_compras'].values
    x = pd.DataFrame(range(1, len(y) + 1), columns=['mes'])
    xFuturo = pd.DataFrame(range(1, len(y) + 13), columns=['mes'])

    reg_model = LinearRegression().fit(x, y)

    previsao = reg_model.predict(xFuturo)

    print("Previsão:")
    print(previsao)

    plt.figure(figsize=(10, 6))
    plt.plot(xFuturo['mes'], previsao, 'b', label='Previsão')
    plt.scatter(x['mes'], y, color='red', label='Dados Reais')
    plt.xlabel('Meses')
    plt.ylabel('Total de Compras')
    plt.title(f'Previsão de Compras para {nome_produto}')
    plt.legend()

    previsao_caminho = os.path.join(app.config['UPLOAD_FOLDER'], f'previsao_compras_{nome_produto}.png')
    plt.savefig(previsao_caminho)
    plt.close()

    previsao_caminho_relativo = f'imagens/previsao_compras_{nome_produto}.png'

    return render_template('previsao_compras.html', previsao_caminho=previsao_caminho_relativo,
                           nome_produto=nome_produto)


@app.route('/grafico_compras')
def grafico_compras():
    if 'email' in session:
        nome_produto = request.args.get('compras')
        dados_produto = obter_dados_compras(nome_produto)

        if dados_produto.empty:
            return "Nenhum dado encontrado para as compras."

        data = dados_produto['data']
        valor = dados_produto['valor']

        plt.figure(figsize=(10, 6))
        plt.plot(data, valor, 'b-', label='Dados Reais')
        plt.xlabel('Data')
        plt.ylabel('Valor')
        plt.title(f'Gráfico de Compras para {nome_produto}')
        plt.legend()
        plt.grid(True)

        graficos_dir = os.path.join(app.static_folder, 'graficos')
        if not os.path.exists(graficos_dir):
            os.makedirs(graficos_dir)

        plt.savefig(os.path.join(graficos_dir, f'{nome_produto}.png'))
        plt.close()

        return render_template('grafico_compras.html', nome_produto=nome_produto)
    else:
        return redirect(url_for('login'))


@app.route('/selecionarProdutoPrevisao', methods=['GET'])
def selecionar_produto_previsao():
    if 'email' in session:
        produtos = listar_produtos()
        for produto in produtos:
            produto['foto_caminho'] = os.path.join(app.config['UPLOAD_FOLDER'],
                                                   os.path.basename(produto['foto_caminho']))
        return render_template('selecionar_produto_previsao.html', produtos=produtos)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
