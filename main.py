#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from functions import login_func, duplicidade_cpf_e_nome, tratamento_paciente_format
from functions import paciente_format, pacientes_tabela, duplicidade_cpf_e_nome
from functions import tratamento_format, tratamentos_tabela, tratamento_edit
from functions import tratamento_paciente_format
from functions import profissional_format

from flask import Flask, render_template, request, redirect, session, flash, url_for
from bd import bd_pacientes, bd_tratamentos, bd_profissional


##################
#### FLASK APP ###
##################

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"


#############
### ROTAS ###
#############

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    return login_func()

# ROTA INDEX/LOGIN
@app.route('/')
def index():
    return render_template('login.html')

# HOME
@app.route('/home')
def home():
    return render_template('home.html')

# LOGOUT
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return render_template('landing_page.html')




############################################## PACIENTE ################################################

@app.route('/paciente-consulta')
def paciente_consulta():
    pacientes_dados = bd_pacientes.find() # dados do banco de dados
    dados = pacientes_tabela(pacientes_dados)
    
    headings = dados[0]
    pacientes = dados[1]

    return render_template('paciente_consulta.html', headings=headings, pacientes=pacientes)

@app.route('/paciente-novo', methods = ['GET', 'POST'])
def paciente_novo():

    if request.method == 'POST':

        form = request.form # pega dos dados do formulario
        response = paciente_format(form) # tranforma os dados em um dict
        cpf = response['cpf'] # cpf do form
        nome = response['nome']

        duplicidade = duplicidade_cpf_e_nome(cpf, nome)

        if duplicidade == True:
            flash("Nome e CPF já está em uso", category="error")
            return redirect(url_for('paciente_novo'))  # faz o redirect para a pagina tratamento-paciente junto com o dado do cpf (para fazer um tratamento obrigatorio atrelado ao paciente recem criado)

        else:
            bd_pacientes.insert_one(response)
            flash("Paciente cadastrado", category="succsses")

        return redirect(url_for('paciente_tratamento', cpf=cpf, nome=nome))  # faz o redirect para a pagina tratamento-paciente junto com o dado do cpf (para fazer um tratamento obrigatorio atrelado ao paciente recem criado)

    return render_template('paciente_novo.html')

@app.route('/paciente-editar', methods=['POST', 'GET'])
def paciente_editar():

    if request.method == 'POST':

        # novos dados do form para update do usuário
        form = request.form
        dados_form = paciente_novo(form)

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
def tratamento_consulta():
    tratamentos_dados = bd_tratamentos.find() # dados do banco de dados
    dados = tratamentos_tabela(tratamentos_dados)
    
    headings = dados[0]
    tratamentos = dados[1]

    return render_template('tratamento_consulta.html', headings=headings, tratamentos=tratamentos)

@app.route('/tratamento-novo', methods = ['GET', 'POST'])
def tratamento_novo():

    if request.method == 'POST':
        form = request.form
        response = tratamento_format(form)
        bd_tratamentos.insert_one(response)    

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect(url_for('tratamento_consulta'))

    return render_template('tratamento_novo.html')

@app.route('/tratamento-editar', methods=['POST', 'GET'])
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





############################################## TRATAMENTO ################################################

@app.route('/profissional-consulta', methods=['POST', 'GET'])
def profissional_consulta():
    profissional_dados = bd_profissional.find() # dados do banco de dados
    dados = pacientes_tabela(profissional_dados)
    
    headings = dados[0]
    profissional = dados[1]

    return render_template('profissional_consulta.html', headings=headings, profissional=profissional)

@app.route('/profissional-novo', methods=['POST', 'GET'])
def profissional_novo():

    if request.method == 'POST':
        profissional_form = request.form
        response = profissional_format(profissional_form)

        # print(response)
        bd_profissional.insert_one(response)
        flash('Profissional cadastrado com sucesso', 'success')
        return redirect(url_for('profissional_consulta'))

    return render_template('profissional_novo.html')

@app.route('/profissional-editar', methods=['POST', 'GET'])
def profissional_editar():
    return render_template('profissional_editar.html')





#################################
############## RUN ##############
#################################
if __name__ == '__main__':
    app.run(debug=True) 