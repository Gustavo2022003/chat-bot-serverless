import boto3
import os
from datetime import datetime
import uuid

TABLE_DYNAMO_PETS = os.getenv('DYNAMODB_TABLE_PETS')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_DYNAMO_PETS)

def get_pets():
    """
    Recupera todos os animais disponíveis na tabela do DynamoDB.

    Realiza uma varredura completa na tabela e retorna todos os itens (animais) encontrados.
    Se nenhum animal for encontrado, retorna `None`.

    Returns:
        list: Lista de animais encontrados ou `None` caso não haja animais.
    """
    try:
        response = table.scan()  # Realiza uma varredura na tabela
        return response.get('Items', None)  # Retorna os animais ou None se não houver resultados
    except Exception as e:
        logger.error(f"Erro ao recuperar animais: {str(e)}")
        return None


def get_pet_by_id(id):
    """
    Recupera um animal específico pelo seu ID a partir do DynamoDB.

    A função busca um animal na tabela utilizando o ID fornecido.
    Se o animal for encontrado, retorna o item correspondente. Caso contrário, retorna `None`.

    Args:
        id (str): O ID do animal a ser recuperado.

    Returns:
        dict: O item do animal encontrado ou `None` se o animal não existir.
    """
    try:
        # Recupera o animal pela chave primária 'id'
        response = table.get_item(Key={'id': id})
        return response.get('Item', None)  # Retorna o item do animal ou None
    except Exception as e:
        logger.error(f"Erro ao buscar animal com ID {id}: {str(e)}")
        return None

def get_pet_by_name_and_breed(name, breed):
    """
    Recupera um animal específico a partir do seu nome e raça.

    A função realiza uma consulta usando o índice secundário para buscar um animal pelo nome.
    Após encontrar os animais com o nome correspondente, a função filtra pela raça especificada.

    Args:
        name (str): O nome do animal a ser buscado.
        breed (str): A raça do animal a ser buscada.

    Returns:
        dict: O animal encontrado ou `None` caso não exista.
    """
    try:
        # Realiza uma consulta no índice secundário para buscar pelo nome do animal
        response = table.query(
            IndexName='NameIndex',  # Usando índice secundário de nome
            KeyConditionExpression=boto3.dynamodb.conditions.Key('nome').eq(name)
        )
        
        # Itera sobre os itens retornados e filtra pela raça
        for pet in response.get('Items', []):
            if pet.get('raça') == breed:
                return pet  # Retorna o pet encontrado
        
        return None  # Retorna None se não encontrar o pet com a raça especificada
    except Exception as e:
        logger.error(f"Erro ao buscar animal com nome {name} e raça {breed}: {str(e)}")
        return None


def insert_pet(name, specie, breed, age):
    """
    Insere um novo animal na tabela do DynamoDB.

    A função gera um ID único para o novo animal, preenche os dados do animal, e os insere na tabela.
    O status do animal é definido como "disponível" por padrão.

    Args:
        name (str): O nome do animal.
        specie (str): A espécie do animal.
        breed (str): A raça do animal.
        age (int): A idade do animal.

    Returns:
        dict: A resposta da operação de inserção no DynamoDB.
    """
    try:
        # Gera um UUID para o novo animal e insere os dados na tabela
        response = table.put_item(Item={
            'id': str(uuid.uuid4()),  # Gera um ID único para o animal
            'nome': name,
            'especie': specie,
            'raça': breed,
            'idade': age,
            'disponivel': True,  # O animal é marcado como disponível por padrão
        })
        return response  # Retorna a resposta da operação de inserção
    except Exception as e:
        logger.error(f"Erro ao inserir animal {name}: {str(e)}")
        return None