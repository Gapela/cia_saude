#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from functions import login_func, paciente_novo, pacientes_tabela, tratamentos_tabela
from flask import Flask, render_template, request, redirect, session, flash
from bd import bd_pacientes, bd_tratamentos
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

#######################################
########### EDITAR PACIENTE ###########
#######################################
@app.route('/paciente-editar', methods=['POST', 'GET'])
def paciente_editar():
    return render_template('paciente_editar.html')

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

################################
########### PACIENTE ###########
################################
@app.route('/paciente', methods = ['GET', 'POST'])
def paciente():

    if request.method == 'POST':
        paciente = request.form

        response = paciente_novo(paciente)
        bd_pacientes.insert_one(response)    

        flash('Paciente cadastrado com sucesso!', category='success')
        return redirect('/tratamento-paciente')
    
    return render_template('paciente.html')

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

##################################
########### TRATAMENTO ###########
##################################
@app.route('/tratamento', methods = ['GET', 'POST'])
def tratamento():

    if request.method == 'POST':

        # tranforma o retorno do post form em um dict
        tratamento_dict = request.form.to_dict()
        
        # Inserir o novo usuário no banco de dados
        bd_tratamentos.insert_one(tratamento_dict)

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect('/consulta')

    return render_template('tratamento.html')

#########################################
########### EDITAR TRATAMENTO ###########
#########################################
@app.route('/tratamento-editar', methods=['POST', 'GET'])
def tratamento_editar():
    return render_template('tratamento_editar.html')

###########################################
########### TRATAMENTO-PACIENTE ###########
###########################################
@app.route('/tratamento-paciente', methods = ['GET','POST'])
def tratamento_paciente():

    if request.method == 'POST':

        # tranforma o retorno do post form em um dict
        tratamento_dict = request.form.to_dict()

        # Inserir o novo usuário no banco de dados
        bd_tratamentos.insert_one(tratamento_dict)

        flash('Tratamento cadastrado com sucesso!', category='success')
        return redirect('/consulta')

    return render_template('tratamento_sync_paciente.html')

#################################
############## RUN ##############
#################################
if __name__ == '__main__':
    app.run(debug=True)