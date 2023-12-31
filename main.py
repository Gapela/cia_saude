#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from functions import duplicidade_cpf_e_nome, tratamento_paciente_format
from functions import paciente_format, pacientes_tabela, duplicidade_cpf_e_nome
from functions import tratamento_format, tratamentos_tabela, tratamento_edit
from functions import tratamento_paciente_format
from functions import profissional_format
from functions import replace_none_with_empty
from functions import paciente_upload_s3, profissional_upload_s3

from bd import bd_pacientes, bd_tratamentos, bd_profissional, bd_usuarios

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask import Flask, render_template, request, redirect, flash, url_for

import bcrypt
import os


##################
#### FLASK APP ###
##################

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Configurar o diretório 'static' para servir arquivos estáticos
app.static_folder = 'static'

# configuração da AWS S3
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AKIAVCIOU2LHPI4NYVV3')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('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')
app.config['AWS_REGION'] = 'sa-east-1'
app.config['S3_BUCKET'] = 'ciasaude'

###################
### FLASK LOGIN ###
###################

# LOGIN MANAGER
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# USER MIXIN
# Classe do Usuário
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


#############
### ROTAS ###
#############

# ROTA INDEX/LOGIN
@app.route('/')
def index():
    return redirect(url_for('login'))

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = bd_usuarios.find_one({'username': username})

        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
            user = User(user_data['username'])
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html')

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# HOME
@app.route('/home')
@login_required
def home():
    return render_template('home.html')


############################################## PACIENTE ################################################

@app.route('/paciente-consulta')
@login_required
def paciente_consulta():
    pacientes_dados = bd_pacientes.find() # dados do banco de dados
    dados = pacientes_tabela(pacientes_dados)
    
    pacientes = dados[1]

    # Substituir valores "None" por " "
    pacientes = replace_none_with_empty(pacientes)  

    return render_template('paciente_consulta.html', pacientes=pacientes)

@app.route('/paciente-novo', methods = ['GET', 'POST'])
@login_required
def paciente_novo():

    if request.method == 'POST':

        form = request.form # pega dos dados do formulario
        response = paciente_format(form) # tranforma os dados em um dict

        cpf = response['cpf']
        nome = response['nome']

        duplicidade = duplicidade_cpf_e_nome(cpf, nome)

        if duplicidade == True:
            flash("Nome e CPF já está em uso", category="error")
            return redirect(url_for('paciente_novo'))  # faz o redirect para a pagina tratamento-paciente junto com o dado do cpf (para fazer um tratamento obrigatorio atrelado ao paciente recem criado)

        else:
            bd_pacientes.insert_one(response)
            paciente_upload_s3(app)
            flash("Paciente cadastrado", category="succsses")

        return redirect(url_for('paciente_tratamento', cpf=cpf, nome=nome))  # faz o redirect para a pagina tratamento-paciente junto com o dado do cpf (para fazer um tratamento obrigatorio atrelado ao paciente recem criado)

    return render_template('paciente_novo.html')

@app.route('/paciente-editar', methods=['POST', 'GET'])
@login_required
def paciente_editar():

    if request.method == 'POST':

        # novos dados do form para update do usuário
        form = request.form
        dados_form = paciente_format(form)

        # criação de variaveis para o find_one_and_update do pymongo
        dados_url = request.args # argumento 'cpf' passa na url
        cpf_url = dados_url['cpf']

        filtro = {'cpf': cpf_url}
        novos_dados = {'$set': dados_form}

        # update dos dados no mongodb
        update = bd_pacientes.find_one_and_update(filtro, novos_dados)

        if update:
            flash('Paciente editado com sucesso.', category='success') # exibe msg no front de sucesso de cadastro
            update
        else:
            flash('Paciente não editado.', category='error') # exibe msg no front de sucesso de cadastro
        
        return redirect(url_for('paciente_consulta'))
    
    return render_template('paciente_editar.html')



############################################## PACIENTE/TRATAMENTO ################################################

###########################################
########### TRATAMENTO-PACIENTE ###########
###########################################
@app.route('/paciente-tratamento', methods = ['GET','POST'])
@login_required
def paciente_tratamento():
    '''
    este é o tratamento que é carregado logo após o cadastro de um novo paciente.
    pois um tratamento é requerido caso um paciente seja cadastrado.
    '''

    nome_arg = request.args.get('nome')  # pega o nome da url
    cpf_arg = request.args.get('cpf')  # pega o cpf da url

    if request.method == 'POST':

        # tranforma o retorno do post form em um dict
        form = request.form
        response = tratamento_paciente_format(nome_arg, cpf_arg, form)

        # Inserir o novo usuário no banco de dados
        bd_tratamentos.insert_one(response)

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect(url_for('tratamento_consulta'))

    return render_template('paciente_tratamento.html')



############################################## TRATAMENTO ################################################

@app.route('/tratamento-consulta')
@login_required
def tratamento_consulta():
    tratamentos_dados = bd_tratamentos.find() # dados do banco de dados
    dados = tratamentos_tabela(tratamentos_dados)

    tratamentos = dados[1]

    # Substituir valores "None" por " "
    tratamentos = replace_none_with_empty(tratamentos)

    return render_template('tratamento_consulta.html', tratamentos=tratamentos)

@app.route('/tratamento-novo', methods = ['GET', 'POST'])
@login_required
def tratamento_novo():

    if request.method == 'POST':
        form = request.form
        response = tratamento_format(form)
        print(response)
        bd_tratamentos.insert_one(response)

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect(url_for('tratamento_consulta'))

    return render_template('tratamento_novo.html')

@app.route('/tratamento-editar', methods=['POST', 'GET'])
@login_required
def tratamento_editar():

    if request.method == 'POST':

        # novos dados do form para update do usuário
        form = request.form
        dados_form = tratamento_edit(form)

        # criação de variaveis para o find_one_and_update do pymongo
        dados_url = request.args # argumento 'cpf' passa na url
        cpf_url = dados_url['cpf']

        filtro = {'cpf': cpf_url}
        novos_dados = {'$set': dados_form}

        # update dos dados no mongodb
        update = bd_tratamentos.find_one_and_update(filtro, novos_dados)

        if update:
            flash('Tratamento editado com sucesso.', category='success') # exibe msg no front de sucesso de cadastro
            update
        else:
            flash('Tratamento não editado.', category='error') # exibe msg no front de sucesso de cadastro

        return redirect(url_for('tratamento_consulta'))

    return render_template('tratamento_editar.html')



############################################## PROFISSIONAL ################################################

@app.route('/profissional-consulta')
@login_required
def profissional_consulta():
    profissional_dados = bd_profissional.find() # dados do banco de dados

    profissional = pacientes_tabela(profissional_dados)[1]

    # Substituir valores "None" por " "
    profissional = replace_none_with_empty(profissional)

    return render_template('profissional_consulta.html', profissional=profissional)

@app.route('/profissional-novo', methods=['POST', 'GET'])
@login_required
def profissional_novo():

    if request.method == 'POST':
        profissional_form = request.form
        response = profissional_format(profissional_form)

        # print(response)
        bd_profissional.insert_one(response)
        profissional_upload_s3(app)
        flash('Profissional cadastrado com sucesso', 'success')
        return redirect(url_for('profissional_consulta'))

    return render_template('profissional_novo.html')

@app.route('/profissional-editar', methods=['POST', 'GET'])
@login_required
def profissional_editar():

    if request.method == 'POST':

        # novos dados do form para update do profissional
        form = request.form
        dados_form = profissional_format(form)

        # criação de variaveis para o find_one_and_update do pymongo
        dados_url = request.args # argumento 'cpf' passa na url
        cpf_url = dados_url['cpf']

        # dados para serem passados no find_one_and_update
        filtro = {'cpf': cpf_url}
        novos_dados = {'$set': dados_form}

        # update dos dados no mongodb
        update = bd_profissional.find_one_and_update(filtro, novos_dados)

        if update:
            flash('Profissional editado com sucesso.', category='success') # exibe msg no front de sucesso de cadastro
            update
        else:
            flash('Profissional não editado.', category='error') # exibe msg no front de sucesso de cadastro
        
        return redirect(url_for('profissional_consulta'))
    
    return render_template('profissional_editar.html')



#################################
############## RUN ##############
#################################
if __name__ == '__main__':
    app.run(debug=True) 