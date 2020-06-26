from flask import Flask, request
from google.cloud import datastore
from validacao import valida_email, validaTelefone, validaIdade, validaLogin_Usuario, validaEmail_CPF_Repetido
from jsonschema import validate
from validate_docbr import CPF
import json_schemas
import re

db = datastore.Client()
app = Flask(__name__)
cpf = CPF()

@app.route("/account", methods=["POST"])
#método de cadastro do usuário
def cadastraUsuario():
    #validação de dados do campo authorization
    if request.authorization and request.authorization.username and request.authorization.password:
        requisicao = request.get_json()
        #validação do schema json
        try:
            validate(requisicao, json_schemas.schema_user)
            validate(requisicao["address"], json_schemas.schema_address)
        except:
            return {"message": "Dados inválidos"}, 400
            
        #formatação padrão de alguns dados
        requisicao["document"] = re.sub(r'\W', '', requisicao["document"])
        requisicao["document"] = re.sub(r'\s', '', requisicao["document"])
        requisicao["email"] = re.sub(r'\s', '', request.authorization.username)
        requisicao["address"]["zipcode"] = re.sub(r'\s', '', requisicao["address"]["zipcode"])
        requisicao["address"]["zipcode"] = re.sub(r'\W', '', requisicao["address"]["zipcode"])

        #validação CPF repetido
        if validaEmail_CPF_Repetido(requisicao["document"], False) == True:
            #validação E-mail repetido
            if validaEmail_CPF_Repetido(False, requisicao["email"]) == True:
                #validação de CPF
                if cpf.validate(requisicao["document"]) == False:
                    return {"message": "Dados inválidos"}, 400
                #validação de E-mail
                elif valida_email(requisicao["email"]) == False:
                    return {"message": "E-mail inválido"}, 406
                #validação de telelefone
                elif validaTelefone(requisicao["phone"]) == False:
                    return {"message": "Dados inválidos"}, 400
                #valida se o usuário tem a idade correta
                elif validaIdade(requisicao["birthDate"]) == False:
                    return {"message": "Dados inválidos"}, 400
                else:
                    requisicao["password"] = request.authorization.password

                    if id in requisicao:
                        del requisicao["id"]

                    with db.transaction():
                        entidade = datastore.Entity(key=db.key("cliente"))
                        entidade.update(requisicao)
                        db.put(entidade)
                    #adiciona os dados no banco

                    entidade["id"] = entidade.key.id
                    del entidade["password"]

                    return {"message": "Usuário cadastrado!", "data": entidade}, 200
            else:
                return {"message": "E-mail já cadastrado"}, 409
        else:
            return {"message": "Dados inválidos"}, 409
    else:
        return {"message": "Dados inválidos"}, 400


@app.route("/account/<id>", methods=["GET"])
#método de consulta de usuário
def consultaUsuario(id):
    if id:
        id = int(id)
        #validação se o campo authorization existe
        if request.authorization and request.authorization.username and request.authorization.password:

            #valida se o usuário existe no banco ou se a senha e usuário dele está correta
            if validaLogin_Usuario(request.authorization.username, request.authorization.password, id) == "Usuario não encontrado":
                return {"message" : "Usuário não encontrado"}, 404
            elif validaLogin_Usuario(request.authorization.username, request.authorization.password, id) == "E-mail ou senha incorreto":
                return {"message" : "Não autorizado"}, 401
            else:
                #consulta usuário
                consultaUsuario = db.get(db.key("cliente", id))
                consultaUsuario['id'] = id
                del consultaUsuario['password']
                return {"message" : "Usuário cadastrado", "data" : consultaUsuario}, 200
        else:
            return {"message" : "Não autorizado"}, 401
    else:
        return {"message" : "Não autorizado"}, 401

@app.route("/account/<id>", methods=["PUT"])
#método de atualização de cadastro
def alteraUsuario(id):
    if id:
        id = int(id)
        #valida se o campo authorization existe
        if request.authorization and request.authorization.username and request.authorization.password:

            #valida se usuário e senha estão corretos
            if validaLogin_Usuario(request.authorization.username, request.authorization.password, id) == "E-mail ou senha incorreto":
                return {"message" : "Não autorizado"}, 401
            elif validaLogin_Usuario(request.authorization.username, request.authorization.password, id) == "Usuario não encontrado":
                return {"message": "Dados inválidos"}, 400
            else:
                requisicao = request.get_json()

                #valida o schema json
                try:
                    validate(requisicao, json_schemas.schema_user)
                    validate(requisicao["address"], json_schemas.schema_address)
                except:
                    return {"message": "Dados inválidos"}, 400

                #padronização de alguns dados
                requisicao["document"] = re.sub(r'\W', '', requisicao["document"])
                requisicao["document"] = re.sub(r'\s', '', requisicao["document"])
                requisicao["email"] = re.sub(r'\s', '', requisicao["email"])
                requisicao["address"]["zipcode"] = re.sub(r'\s', '', requisicao["address"]["zipcode"])
                requisicao["address"]["zipcode"] = re.sub(r'\W', '', requisicao["address"]["zipcode"])

                consultaUsuario = db.get(db.key("cliente", id))

                #valida se o e-mail já existe no banco
                if consultaUsuario["email"] != requisicao["email"]:
                    if validaEmail_CPF_Repetido(False, requisicao["email"]) == False:
                        return {"message" : "E-mail já cadastrado"}, 409

                #valida se o CPF já existe no banco
                if consultaUsuario["document"] != requisicao["document"]:
                    if validaEmail_CPF_Repetido(requisicao["document"], False) == False:
                        return {"message" : "Dados inválidos"}, 400

                #valida o CPF
                if cpf.validate(requisicao["document"]) == False:
                    return {"message": "Dados inválidos"}, 400
                #valida o E-mail
                elif valida_email(requisicao["email"]) == False:
                    return {"message": "E-mail inválido"}, 406
                #valida o telefone
                elif validaTelefone(requisicao["phone"]) == False:
                    return {"message": "Dados inválidos"}, 400
                #valida a idade do usuário
                elif validaIdade(float(requisicao["birthDate"])) == False:
                    return {"message": "Dados inválidos"}, 400
                else:
                    if id in requisicao:
                        del requisicao["id"]
                    #atualiza os dados
                    with db.transaction():
                        entidade = datastore.Entity(db.key("cliente", int(id)))
                        entidade.update(requisicao)
                        entidade["password"] = request.authorization.password
                        db.put(entidade)

                    entidade["id"] = entidade.key.id
                    del entidade["password"]

                    return {"message": "Usuário atualizado!", "data": entidade}, 204
        else:
            return {"message" : "Não autorizado"}, 401
    else:
        return {"message" : "Não autorizado"}, 401

if __name__ == '__main__':
    app.run(debug=True)