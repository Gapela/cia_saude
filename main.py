#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from functions import login_func, paciente_novo, tratamento_novo, pacientes_tabela, tratamentos_tabela, tratamento_edit, duplicidade_cpf, duplicidade_cpf_e_nome
from flask import Flask, render_template, request, redirect, session, flash, url_for
from bd import bd_pacientes, bd_tratamentos
import jsonify
import os


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

#########################################
########### CONSULTA PACIENTE ###########
#########################################
@app.route('/consulta-pacientes')
def consulta_pacientes():
    pacientes_dados = bd_pacientes.find() # dados do banco de dados
    dados = pacientes_tabela(pacientes_dados)
    
    headings = dados[0]
    pacientes = dados[1]

    return render_template('paciente_consulta.html', headings=headings, pacientes=pacientes)

#####################################
########### NOVO PACIENTE ###########
#####################################
@app.route('/paciente', methods = ['GET', 'POST'])
def paciente():

    if request.method == 'POST':

        form = request.form # pega dos dados do formulario
        response = paciente_novo(form) # tranforma os dados em um dict
        cpf = response['cpf'] # cpf do form
        nome = response['nome']

        duplicidade = duplicidade_cpf_e_nome(cpf, nome)

        if duplicidade == True:
            flash("Nome e CPF já está em uso", category="error")
            return redirect(url_for('paciente'))  # faz o redirect para a pagina tratamento-paciente junto com o dado do cpf (para fazer um tratamento obrigatorio atrelado ao paciente recem criado)

        else:
            bd_pacientes.insert_one(response)
            flash("Paciente cadastrado", category="succsses")

        return redirect(url_for('tratamento_paciente', cpf=cpf, nome=nome))  # faz o redirect para a pagina tratamento-paciente junto com o dado do cpf (para fazer um tratamento obrigatorio atrelado ao paciente recem criado)

    return render_template('paciente.html')

#######################################
########### EDITAR PACIENTE ###########
#######################################
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
        
        return redirect('/consulta-pacientes')
    
    return render_template('paciente_editar.html')


############################################## PACIENTE/TRATAMENTO ################################################

###########################################
########### TRATAMENTO-PACIENTE ###########
###########################################
@app.route('/tratamento-paciente', methods = ['GET','POST'])
def tratamento_paciente():
    '''
    este é o tratamento que é carregado logo após o cadastro de um novo paciente.
    pois um tratamento é requerido caso um paciente seja cadastrado.
    '''

    cpf = request.args.get('cpf')  # pega o cpf da url

    if request.method == 'POST':

        # tranforma o retorno do post form em um dict
        tratamento_dict = request.form.to_dict()

        # Inserir o novo usuário no banco de dados
        bd_tratamentos.insert_one(tratamento_dict)

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect('/consulta-tratamentos')

    return render_template('tratamento_sync_paciente.html', cpf=cpf)













############################################## TRATAMENTO ################################################

###########################################
########### CONSULTA TRATAMENTO ###########
###########################################
@app.route('/consulta-tratamentos')
def consulta_tratamentos():
    tratamentos_dados = bd_tratamentos.find() # dados do banco de dados
    dados = tratamentos_tabela(tratamentos_dados)
    
    headings = dados[0]
    tratamentos = dados[1]

    return render_template('tratamento_consulta.html', headings=headings, tratamentos=tratamentos)

#######################################
########### NOVO TRATAMENTO ###########
#######################################
@app.route('/tratamento', methods = ['GET', 'POST'])
def tratamento():

    if request.method == 'POST':
        tratamento = request.form

        response = tratamento_novo(tratamento)

        print(response)
  
        bd_tratamentos.insert_one(response)    

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect('/consulta-tratamentos')

    return render_template('tratamento.html')

#########################################
########### EDITAR TRATAMENTO ###########
#########################################
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
        
        return redirect('/consulta-tratamentos')

    return render_template('tratamento_editar.html')









#################################
############## RUN ##############
#################################
if __name__ == '__main__':
    app.run(debug=True) 