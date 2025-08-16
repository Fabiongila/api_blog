from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps



def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token= request.headers['x-access-token']
        if not token:
            return jsonify({'Mensagem': 'Token não foi incluído'}, 401)
        # Se temos um token, validar o acesso ao db
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print(resultado)
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except Exception:
            print(Exception)
            return jsonify({'Mensagem': 'Token é inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401,  {'WWW-Authenticate': 'Basic realm ="Login obrigatório"'})
    usuário = Autor.query.filter_by(nome= auth.username).first()
    if not usuário:
         return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm ="Login obrigatório"'})
    if auth.password == usuário.senha:
        global token
        token = jwt.encode({'id_autor': usuário.id_autor, 'exp':datetime.now(timezone.utc) + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
        
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm ="Login obrigatório"'})


# API Postagem

#Rota padrão - GET  http://localhost:500
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_postagens.append(postagem_atual)

    return jsonify({'Postagens': lista_postagens})


#Rota - GET com id -  http://localhost:500/postagens/1
@app.route('/postagens/<int:id_postagem>', methods = ['GET'])
@token_obrigatorio
def obter_postagens_po_incice(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify('Postagem não encontrada')
    postagem_actual = {}
    postagem_actual['id_postagem'] = postagem.id_postagem
    postagem_actual['titulo'] = postagem.titulo
    postagem_actual['autor'] = postagem.id_autor
    
    return jsonify({'Postagem': postagem_actual})


#Criar uma nova postagem - POST - http://localhost:500/postagens
@app.route('/postagens', methods = ['POST'])
@token_obrigatorio
def nova_postagem(autor):
    novo_autor = request.get_json()
    postagem = Postagem(
        titulo = novo_autor['titulo'], id_autor = novo_autor['id_autor']
    )
    db.session.add(postagem)
    db.session.commit()

    return jsonify({'Mensagem': 'Postagem criada com sucesso'})


# Alterar um recurso/postagem existente - PUT - http://localhost:500/postagens/1
@app.route('/postagens/<int:id_postagem>', methods = ['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_a_alterar = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem = id_postagem).first()
    if not postagem:
        return jsonify('Postagem não encontrada')
    try:
        postagem.titulo = postagem_a_alterar['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_a_alterar['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'Mensagem': 'Postagem alterada com sucesso'})


# Excluir postagem - DELETE -  http://localhost:500/postagens/2
@app.route('/postagens/<int:id_postagem>', methods =['DELETE'])
@token_obrigatorio
def excluir_postagem(autor, id_postagem):
   postagem_existente = Postagem.query.filter_by(id_postagem=id_postagem).first()
   if not postagem_existente:
       return jsonify({'Mendagem': 'Esta postagem não foi enconntrada'})
   db.session.delete(postagem_existente)
   db.session.commit()

   return jsonify({'Mensagem': 'Postagem excluida comsucesso!'})


# API Autores
@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        autor_atual['id_autor'] = autor.id_autor
        lista_autores.append(autor_atual)

    return jsonify({'autores':lista_autores})

@app.route('/autores/<int:id_autor>', methods =['GET'])
@token_obrigatorio
def obter_autor_por_id(autor, id_autor):
   autor = Autor.query.filter_by(id_autor = id_autor).first()
   if not autor:
       return jsonify(f'Autor não enontrado')
   autor_atual = {}
   autor_atual['id_autor'] = autor.id_autor
   autor_atual['nome'] = autor.nome
   autor_atual['email'] = autor.email

   return jsonify({'autor': autor_atual})

@app.route('/autores', methods =['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(
        nome= novo_autor['nome'], senha= novo_autor['senha'],
         email = novo_autor['email'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso!'}, 200)

@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'Mensagem': 'Este usuário ñao foi encontrado'})
    try:
        autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
        autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        autor.senha = usuario_a_alterar['senha']
    except:
        pass

    db.session.commit()
    return jsonify({'Mensagem': 'Usuário alterado com sucesso!'})


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente =Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'Mensagem': 'Este autor não foi encontrado'})
    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify('Autor excluido com sucesso')









app.run(port=500, host='localhost', debug=True )