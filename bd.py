#################################################################################################
############################################ IMPORTS ############################################
#################################################################################################
from pymongo import MongoClient

##################################################################################################
############################################ DATABASE ############################################
##################################################################################################
bd_user = "gpelai"
bd_password = "4e129757"
client = MongoClient(f'mongodb+srv://{bd_user}:{bd_password}@cluster0.v1wbgmq.mongodb.net/?retryWrites=true&w=majority')
bd = client.clinica

###################
### COLLECTIONS ###
###################
bd_usuarios = bd.usuarios
bd_pacientes = bd.pacientes
bd_tratamentos = bd.tratamentos
bd_profissional = bd.profissional