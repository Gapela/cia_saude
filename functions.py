#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from flask import request, redirect, session, flash, jsonify
from bd import bd_pacientes, bd_usuarios
from datetime import datetime
from time import sleep
import pandas as pd
import bcrypt
import boto3

#################################################################################################
############################################ FUNÇÕES ############################################
#################################################################################################

############# UPLOAD S3 ####################
def paciente_upload_s3(app):

    file = request.files['anexo']
    
    if file:
        s3 = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION']
        )

        # Obtenha o nome do arquivo a partir do objeto de arquivo (file)
        file_key = f"paciente/{file.filename}"
        s3.upload_fileobj(file, app.config['S3_BUCKET'], file_key)

        # Você pode armazenar a URL do arquivo no banco de dados ou retorná-la como resposta
        file_url = f'https://{app.config["S3_BUCKET"]}.s3.amazonaws.com/{file_key}'

        return jsonify({'file_url': file_url})

    return jsonify({'error': 'Erro no upload do arquivo'}), 400

def profissional_upload_s3(app):

    file = request.files['anexo']
    
    if file:
        s3 = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION']
        )

        # Obtenha o nome do arquivo a partir do objeto de arquivo (file)
        file_key = f"profissional/{file.filename}"
        s3.upload_fileobj(file, app.config['S3_BUCKET'], file_key)

        # Você pode armazenar a URL do arquivo no banco de dados ou retorná-la como resposta
        file_url = f'https://{app.config["S3_BUCKET"]}.s3.amazonaws.com/{file_key}'

        return jsonify({'file_url': file_url})

    return jsonify({'error': 'Erro no upload do arquivo'}), 400

################ login ####################
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

def duplicidade_cpf_e_nome(cpf, nome):

    user = bd_pacientes.find_one({'$and': [{'cpf': cpf}, {'nome': nome}]})

    if user:
        status = True
    else:
        status = False

    # return cpf_status
    return status

def replace_none_with_empty(data):
    return [['' if value is None else value for value in row] for row in data]


########################################### PACIENTE ##############################
# paciente novo
def paciente_format(paciente_form):

    # variaveis do form
    nome = paciente_form.get('nome')
    endereco = paciente_form.get('endereco')
    cep = paciente_form.get('cep')
    rg = paciente_form.get('rg')
    cpf = paciente_form.get('cpf')
    telefone = paciente_form.get('telefone')
    email = paciente_form.get('email')
    data_nascimento_str = paciente_form.get('data_nascimento')
    responsavel = paciente_form.get('responsavel')
    medico_solicitante = paciente_form.get('medico_solicitante')
    crm = paciente_form.get('crm')
    ocupacao = paciente_form.get('ocupacao')
    cid = paciente_form.get('cid')
    observacao = paciente_form.get('observacao')
    numero_carteirinha = paciente_form.get('numero_carteirinha')
    plano = paciente_form.get('plano')

    # regra para não pegar o valor "Selecione uma opção"
    if paciente_form.get('pagamento') == 'Selecione uma opção':
        pagamento = ""
    if paciente_form.get('pagamento') != 'Selecione uma opção':
        pagamento = paciente_form.get('pagamento')
        
    if paciente_form.get('empresa') == 'Selecione uma opção':
        empresa = ""
    if paciente_form.get('empresa') != 'Selecione uma opção':
        empresa = paciente_form.get('empresa')

    # formata a data nascimento
    formato_entrada = "%Y-%m-%d"
    formato_saida = "%d/%m/%Y"
    data_nascimento = datetime.strptime(data_nascimento_str, formato_entrada)
    data_nascimento_formatada = datetime.strftime(data_nascimento, formato_saida)


    response = {
        'nome': nome,
        'endereco': endereco,
        'cep': cep,
        'rg': rg,
        'cpf': cpf,
        'telefone': telefone,
        'email': email,
        'data_nascimento': data_nascimento_formatada,
        'responsavel': responsavel,
        'medico_solicitante': medico_solicitante,
        'crm': crm,
        'ocupacao': ocupacao,
        'cid': cid,
        'observacao': observacao,
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


########################################### PACIENTE / TRATAMENTO ##############################
# tratamento novo (muda todos os dados)
def tratamento_paciente_format(nome, cpf, form):

    # variaveis do form
    nome = nome
    cpf = cpf
    especialidade = form.get('especialidade')
    profissional_responsavel = form.get('profissional_responsavel')
    observacao = form.get('observacao')
    data_inicio_str = form.get('data_inicio')
    data_fim_str = form.get('data_fim')

    # formata as datas
    formato_entrada = "%Y-%m-%d"
    formato_saida = "%d/%m/%Y"

    if(data_inicio_str):
        data_inicio = datetime.strptime(data_inicio_str, formato_entrada)
        data_inicio_formatada = data_inicio.strftime(formato_saida)
    else:
        data_inicio_formatada = ""

    if(data_fim_str):
        data_fim = datetime.strptime(data_fim_str, formato_entrada)
        data_fim_formatada = data_fim.strftime(formato_saida)
    else:
        data_fim_formatada = ""

    response = {
        'nome': nome,
        'cpf': cpf, 
        'especialidade': especialidade,
        'profissional_responsavel': profissional_responsavel,
        'observacao': observacao,
        'data_inicio': data_inicio_formatada,
        'data_fim': data_fim_formatada
    }

    return response


########################################### TRATAMENTO ##############################

# tratamento novo (muda todos os dados)
def tratamento_format(tratamento_form):

    # variaveis do form
    nome = tratamento_form.get('nome')
    cpf = tratamento_form.get('cpf')
    especialidade = tratamento_form.get('especialidade')
    profissional_responsavel = tratamento_form.get('profissional_responsavel')
    observacao = tratamento_form.get('observacao')
    data_inicio_str = tratamento_form.get('data_inicio')
    data_fim_str = tratamento_form.get('data_fim')

    # formata as datas
    formato_entrada = "%Y-%m-%d"
    formato_saida = "%d/%m/%Y"

    if (data_inicio_str):
        data_inicio = datetime.strptime(data_inicio_str, formato_entrada)
        data_inicio_formatada = data_inicio.strftime(formato_saida)
    else:
        data_inicio_formatada = ""
        
    if (data_fim_str):
        data_fim = datetime.strptime(data_fim_str, formato_entrada)
        data_fim_formatada = data_fim.strftime(formato_saida)
    else:
        data_fim_formatada = ""
    


    response = {
        'nome': nome,
        'cpf': cpf, 
        'especialidade': especialidade,
        'profissional_responsavel': profissional_responsavel,
        'observacao': observacao,
        'data_inicio': data_inicio_formatada,
        'data_fim': data_fim_formatada
    }

    return response

# tratamento novo (muda somente "Data_fim")
def tratamento_edit(tratamento_form):

    # variaveis do form
    data_fim_str = tratamento_form.get('data_fim')

    # formata as datas
    formato_entrada = "%Y-%m-%d"
    formato_saida = "%d/%m/%Y"

    # formata a data_fim        
    if (data_fim_str):
        data_fim = datetime.strptime(data_fim_str, formato_entrada)
        data_fim_formatada = data_fim.strftime(formato_saida)
    else:
        data_fim_formatada = ""

    response = {
        'data_fim': data_fim_formatada
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


########################################### PROFISSISONAL ##############################

def profissional_format(profissional_form):
    
    # variaveis do form
    nome = profissional_form.get('nome')
    endereco = profissional_form.get('endereco')
    rg = profissional_form.get('rg')
    cpf = profissional_form.get('cpf')
    telefone = profissional_form.get('telefone')
    especialidade = profissional_form.get('especialidade')
    obs_especializacao = profissional_form.get('obs_especializacao')
    crm = profissional_form.get('crm')
    pagamento = profissional_form.get('pagamento')
    empresa = profissional_form.get('empresa')
    plano = profissional_form.get('plano')
    pix = profissional_form.get('pix')
    banco = profissional_form.get('banco')
    agencia = profissional_form.get('agencia')
    conta = profissional_form.get('conta')

    response = {
        'nome': nome,
        'endereco': endereco,
        'rg': rg,
        'cpf': cpf,
        'telefone': telefone,
        'especialidade': especialidade,
        'obs_especializacao': obs_especializacao,
        'crm': crm,
        'pagamento': pagamento,
        'empresa': empresa,
        'plano': plano,
        'pix': pix,
        'banco': banco,
        'agencia': agencia,
        'conta': conta
    }

    return response

def profissional_tabela(bd_profissional):
    profissional_df = pd.DataFrame([x for x in bd_profissional]) # tranforma o dados em uma lista

    if len(profissional_df) > 0:
        df = profissional_df.drop(columns=["_id"])
    else:
        df = profissional_df
    

    pacientes = list(df.values) # faz uma lista dos dados puxados do banco de dados
    return (pacientes)
    # print (pacientes)
