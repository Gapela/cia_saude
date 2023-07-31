#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from flask import request, redirect, session, flash
from bd import bd_tratamentos, bd_pacientes, bd_usuarios
from time import sleep
import pandas as pd
import bcrypt

#################################################################################################
############################################ FUNÇÕES ############################################
#################################################################################################

# faz o DF dos usuários no banco de dados, tranforma em uma pasta excel e retorna uma .xlsx
def export_to_excel():
    pacientes_dados = bd_pacientes.find()
    pacientes_lista = [x for x in pacientes_dados]
    pacientes_df = pd.DataFrame(pacientes_lista)
    data_excel = pacientes_df.to_excel("pacientes_table.xlsx", sheet_name="pacientes")
    return data_excel

# login
def login_func():
    username = request.form['username']
    password = request.form['password']

    # Buscar o usuário no banco de dados
    user = bd_usuarios.find_one({'username': username})

    # Verificar usuário e senha
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['username'] = username
        flash('Login feito com sucesso!', category='success')
        return redirect('/home')
    else:
        flash('Usuário ou senha incorreto!', category='error')
        sleep(2)
        return redirect("/")
    
# paciente novo
def paciente_novo(paciente):

    # variaveis do form
    nome = paciente.get('nome')
    endereco = paciente.get('endereco')
    rg = paciente.get('rg')
    cpf = paciente.get('cpf')
    telefone = paciente.get('telefone')
    email = paciente.get('email')
    data_nascimento = paciente.get('data_nascimento')
    responsavel = paciente.get('responsavel')
    medico_solicitante = paciente.get('medico_solicitante')
    crm = paciente.get('crm')
    ocupacao = paciente.get('ocupacao')
    cid = paciente.get('cid')
    numero_carteirinha = paciente.get('numero_carteirinha')
    plano = paciente.get('plano')

    # regra para não pegar o valor "Selecione uma opção"
    if paciente.get('pagamento') == 'Selecione uma opção':
        pagamento = ""
    if paciente.get('pagamento') != 'Selecione uma opção':
        pagamento = paciente.get('pagamento')
        
    if paciente.get('empresa') == 'Selecione uma opção':
        empresa = ""
    if paciente.get('empresa') != 'Selecione uma opção':
        empresa = paciente.get('empresa')

    response = {
        'nome': nome,
        'endereco': endereco,
        'rg': rg,
        'cpf': cpf,
        'telefone': telefone,
        'email': email,
        'data_nascimento': data_nascimento,
        'responsavel': responsavel,
        'medico_solicitante': medico_solicitante,
        'crm': crm,
        'ocupacao': ocupacao,
        'cid': cid,
        'pagamento': pagamento,
        'empresa': empresa,
        'numero_carteirinha': numero_carteirinha,
        'plano': plano
    }

    return response

# dados para a tabela na pagina Consulta
def pacientes_tabela(bd_pacientes):
    pacientes_df = pd.DataFrame([x for x in bd_pacientes]) # tranforma o dados em uma lista
    

    if len(pacientes_df) > 0:
        # df = pacientes_df.drop(columns=["_id", "endereco", "rg", "email", "responsavel", "medico_solicitante", "crm", "ocupacao", "cid"])
        df = pacientes_df.drop(columns=["_id"])
    else:
        df = pacientes_df

    headings = list(df.columns.values) # pega a prieira linha para fazer uma lista Headings
    pacientes = list(df.values) # faz uma lista dos dados puxados do banco de dados
    return (headings, pacientes)

# tratamento novo (muda todos os dados)
def tratamento_novo(tratamento):

    # variaveis do form
    nome = tratamento.get('nome')
    cpf = tratamento.get('cpf')
    especialidade = tratamento.get('especialidade')
    profissional_responsavel = tratamento.get('profissional_responsavel')
    data_inicio = tratamento.get('data_inicio')
    data_fim = tratamento.get('data_fim')

    response = {
        'nome': nome,
        'cpf': cpf, 
        'especialidade': especialidade,
        'profissional_responsavel': profissional_responsavel,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    }

    return response

# tratamento novo (muda todos os dados)
def tratamento_edit(tratamento):

    # variaveis do form
    data_fim = tratamento.get('data_fim')

    response = {
        'data_fim': data_fim
    }

    return response

# dados para a tabela na pagina Tratamentos
def tratamentos_tabela(bd_tratamentos):
    tratamentos_df = pd.DataFrame([x for x in bd_tratamentos]) # tranforma o dados em uma lista
    if len(tratamentos_df) > 0:
        df = tratamentos_df.drop(columns=["_id"])
    else:
        df = tratamentos_df

    headings = list(df.columns.values) # pega a prieira linha para fazer uma lista Headings
    pacientes = list(df.values) # faz uma lista dos dados puxados do banco de dados
    return (headings, pacientes)

def duplicidade_cpf(cpf):
    '''
    Procura o CPF no banco de dados mongodb e retorna o valor boleano para o resultado.
    '''

    user = bd_pacientes.find_one({'cpf': cpf})

    if user:
        cpf_status = True
    else:
        cpf_status = False

    # return cpf_status
    return cpf_status

def duplicidade_cpf_e_nome(cpf, nome):
    '''
    Procura o CPF e NOME no banco de dados mongodb e retorna o valor boleano para o resultado.
    '''

    user = bd_pacientes.find_one({'$and': [{'cpf': cpf}, {'nome': nome}]})

    if user:
        status = True
    else:
        status = False

    # return cpf_status
    return status