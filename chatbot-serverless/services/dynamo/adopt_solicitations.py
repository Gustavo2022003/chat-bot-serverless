import boto3
import os
from datetime import datetime
import uuid

from services.dynamo.pets import get_pet_by_id
from services.dynamo.user import get_user_by_id

DYNAMODB_TABLE_REQUEST_ADOPT = os.getenv('DYNAMODB_TABLE_REQUEST_ADOPT')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_REQUEST_ADOPT)

def insert_adopt_solicitation(id_pet, phone, id_user):
    """
    Insere uma solicitação de adoção de animal no banco de dados.
    
    Verifica se o animal e o usuário existem, e, caso existam, cria uma nova solicitação
    de adoção com um status 'Pendente'.

    Args:
        id_pet (str): O ID do pet que está sendo adotado.
        phone (str): O telefone do usuário solicitando a adoção.
        id_user (str): O ID do usuário que está fazendo a solicitação.

    Returns:
        dict: Resposta da operação de inserção no banco de dados ou None se falhar.
    """
    
    # Recupera o pet e o usuário a partir dos seus respectivos IDs
    pet = get_pet_by_id(id_pet)
    user = get_user_by_id(id_user)

    # Verifica se tanto o pet quanto o usuário existem
    if not pet or not user:
        return None  # Retorna None caso pet ou usuário não existam

    # Insere a solicitação de adoção na tabela
    response = table.put_item(Item={
        'id': str(uuid.uuid4()),  # Gera um UUID único para a solicitação
        'pet': pet,
        'user': user,
        'dataCriacao': datetime.now().isoformat(),  # Registra a data de criação da solicitação
        'status': 'Pendente',  # Status inicial da solicitação
    })
    
    # Retorna a resposta da inserção
    return response


def get_adopt_solicitations():
    """
    Recupera todas as solicitações de adoção do banco de dados.

    Realiza uma busca completa na tabela de solicitações e retorna os itens encontrados.

    Returns:
        list: Lista de itens de solicitação de adoção ou None se não houver solicitações.
    """
    
    # Realiza a varredura completa na tabela para obter as solicitações
    response = table.scan()

    # Retorna a lista de solicitações ou None caso não haja resultados
    return response.get('Items', None)

