import re
from datetime import datetime, date
from google.cloud import datastore
from validate_docbr import CPF
from email_validator import validate_email, EmailNotValidError
cpf = CPF()
db = datastore.Client()


def valida_email(email):
    try:
        #aplica o método de validação de e-mail e retorna True se é valido e False se não é valido
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validaTelefone(telefone):
    #valida se o número começa com o DDI +55
    if re.search(r'^\+55', telefone) is not None:
        lista_validacao_ddd = [61, 62, 64, 65, 66, 67, 82, 71, 73, 74, 75, 77, 85, 88, 98,
        99, 83, 81, 87, 86, 89, 84, 79, 68, 96, 92, 97, 91, 93, 94, 69, 95, 63, 27,
        28, 31, 32, 33, 34, 35, 37, 38, 21, 22, 24, 11, 12, 13, 14, 15, 16, 17, 18,
        19, 41, 42, 43, 44, 45, 46, 51, 53, 54, 55, 47, 48, 49]
        lista_validacao_numero_fixo = [2, 3, 4, 5]
        lista_validacao_numero_celular = [6, 7, 8, 9]
        telefone = re.sub(r'\W', '', telefone)
        telefone = re.sub(r'\s', '', telefone)
        #números fixos, retorna True se é valido e False se é inválido
        if len(telefone) == 12:
            ddd = telefone[2] + telefone[3]
            numero = telefone[4] + telefone[5] + telefone[6] + telefone[7] + telefone[8] + telefone[9] + telefone[10] + telefone[11]
            #valida se o DDD existe no Brasil
            if int(ddd) in lista_validacao_ddd:
                #valida se o primeiro digito do telefone começa com o range de telefones fixos [2, 3, 4, 5]
                if int(numero[0]) in lista_validacao_numero_fixo:
                    return True
                else:
                    return False
            else:
                return False
        #números móveis, retorna True para válido e False para inválido
        elif len(telefone) == 13:
            ddd = telefone[2] + telefone[3]
            numero = telefone[4] + telefone[5] + telefone[6] + telefone[7] + telefone[8] + telefone[9] + telefone[10] + telefone[11] + telefone[12]
            print("len")
            #valida se o DDD existe no Brasil
            if int(ddd) in lista_validacao_ddd:
                print("ddd")
                #valida se o primeiro digito do celular é digito 9
                if int(numero[0]) == 9:
                    print("digito nove")
                    #valida se o primeiro digito do telefone começa com o range de telefones fixos [6, 7, 8, 9]
                    if int(numero[1]) in lista_validacao_numero_celular:
                        print("numero")
                        return True
                    else:
                        print("else numero")
                        return False
                else:
                    print("else digito nove")
                    return False
            else:
                print("else ddd")
                return False
        return False
    else:
        return False

def validaIdade(datanascimentoTimestamp):
    
    try:
        datanascimento = float(datanascimentoTimestamp)
        datanascimento = datetime.fromtimestamp(datanascimento)
        diaatual = datetime.now()
        #retorna True para maior ou igual a 18 e False para menor de idade
        #valida se o usuário já tem 18 pelos anos
        if diaatual.year - datanascimento.year == 18:
            #valida se é o mês de aniverssário do usuário se ele completa 18 no ano do cadastro
            if diaatual.month - datanascimento.month == 0:
                #valida se é o dia de aniverssário do usuário
                if diaatual.day - datanascimento.day >= 0:
                    return True
                else:
                    return False
            elif diaatual.month - datanascimento.month > 0:
                return True
            else:
                return False
        elif diaatual.year - datanascimento.year > 18:
            return True
        else:
            return False
    except:
        return False

def validaLogin_Usuario(user, password, id_user):
    #consulta o usuário com o id passado na URL
    db = datastore.Client()
    consulta = db.get(db.key('cliente', int(id_user)))
    #Se não achar, retorna "Usuário não encontrado"
    if consulta == None:
        return "Usuario não encontrado"
    else:
        #se encontrar, valida se o usuário e senha estão corretos. Incorreto retorna "E-mail ou senha incorreto", correto retorna True
        if user != str(consulta["email"]):
            return "E-mail ou senha incorreto"
        elif password != str(consulta["password"]):
            return "E-mail ou senha incorreto"
        else:
            return True

def validaEmail_CPF_Repetido(cpf, email):
    #método para verificar se o e-mail ou cpf já estão no banco
    #se foi passado o e-mail, verifica se ele já existe. Retorna True se não exsite, False se existe
    if email != False:
        query_email = db.query(kind="cliente")
        query_email = query_email.add_filter('email', "=", email)
        result_email = list(query_email.fetch())
        
        if len(result_email) > 0:
            return False
        else:
            return True
    #se foi passado o CPF, verifica se ele já existe. Retorna True se não existe, False se existe
    if cpf != False:
        query_document = db.query(kind="cliente")
        query_document = query_document.add_filter('document', '=', cpf)
        result_document = list(query_document.fetch())

        if len(result_document) > 0:
            return False
        else:
            return True