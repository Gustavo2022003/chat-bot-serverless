import boto3
import logging
import json
import os

LEX_SESSIONS_TABLE = os.getenv('DYNAMODB_TABLE_LEX_SESSIONS')
logger = logging.getLogger()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(LEX_SESSIONS_TABLE) 

def get_session(user_id):
    """
    Carrega o estado da sessão para o usuário a partir do DynamoDB.

    A função tenta recuperar os atributos da sessão associados a um `user_id` no DynamoDB.
    Caso a sessão seja encontrada, ela retorna os atributos salvos. Caso contrário, 
    retorna um dicionário vazio.

    Args:
        user_id (str): O ID do usuário para o qual os dados de sessão devem ser recuperados.

    Returns:
        dict: Um dicionário com os atributos da sessão do usuário ou um dicionário vazio se não encontrado.
    """
    try:
        # Recupera o item do DynamoDB usando o user_id como chave primária
        response = table.get_item(Key={'id': user_id})

        if 'Item' in response:
            # Se a sessão existir, retorna os atributos da sessão
            logger.info(f"Sessão carregada para o usuário {user_id}: {response['Item']}")
            return response['Item'].get('sessionAttributes', {})
        else:
            # Caso não exista sessão associada ao usuário, retorna um dicionário vazio
            logger.info(f"Nenhuma sessão existente encontrada para o usuário {user_id}.")
            return {}

    except Exception as e:
        # Caso ocorra um erro ao tentar carregar a sessão, registra o erro
        logger.error(f"Erro ao carregar a sessão do DynamoDB: {str(e)}")
        return {}


def save_session(user_id, session_attributes):
    """
    Salva o estado da sessão para o usuário no DynamoDB.

    A função armazena os atributos da sessão associados a um `user_id` no DynamoDB. 
    Caso a operação de inserção seja bem-sucedida, registra a operação com sucesso.
    
    Args:
        user_id (str): O ID do usuário para o qual os dados de sessão devem ser salvos.
        session_attributes (dict): Um dicionário contendo os atributos da sessão que devem ser salvos.
    
    Returns:
        None
    """
    try:
        # Salva ou atualiza os atributos da sessão no DynamoDB
        table.put_item(Item={
            'id': user_id,
            'sessionAttributes': session_attributes
        })
        # Registra que a sessão foi salva com sucesso
        logger.info(f"Sessão salva para o usuário {user_id}: {session_attributes}")

    except Exception as e:
        # Caso ocorra um erro ao tentar salvar a sessão, registra o erro
        logger.error(f"Erro ao salvar a sessão no DynamoDB: {str(e)}")
