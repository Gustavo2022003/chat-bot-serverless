import os
import json
from services.polly_service import text_to_speech

def identificarCachorro(event):
    """
    Processa a intenção de identificar a probabilidade de uma raça específica para o animal informado.

    Args:
        event (dict): O evento recebido contendo o estado da sessão, intenções e slots do Amazon Lex.

    Returns:
        dict: Payload estruturado para o Amazon Lex com uma mensagem informando a probabilidade
        e áudio correspondente, ou um erro em caso de falha.
    """
    try:
        # Obtém informações da intenção e atributos da sessão
        intent_name = event['sessionState']['intent']['name']
        session_attributes = event['sessionState'].get('sessionAttributes', {})
        slots = event['sessionState']['intent']['slots']

        # Obtém os valores dos slots, usando "Não informado" como padrão
        type_pet = slots.get('typePet', {}).get('value', {}).get('interpretedValue', "Não informado")
        breed_pet = slots.get('racapet', {}).get('value', {}).get('interpretedValue', "Não informado")
        chance_pet = slots.get('chancePet', {}).get('value', {}).get('interpretedValue', "Não informado")

        # Formata a mensagem com a probabilidade
        try:
            chance_percentage = f"{float(chance_pet):.2f}%"
        except ValueError:
            chance_percentage = "Não disponível"

        formatted_message = f"As chances do {type_pet} ser um {breed_pet} é de {chance_percentage}."

        # Gera áudio correspondente à mensagem
        audio_message = text_to_speech(formatted_message)

        # Retorno estruturado para o Amazon Lex
        return {
            "sessionState": {
                "sessionAttributes": session_attributes,
                "dialogAction": {"type": "Close"},
                "intent": {
                    "name": intent_name,
                    "state": "Fulfilled"
                }
            },
            "messages": [
                {
                    "contentType": "CustomPayload",
                    "content": json.dumps({"audio": audio_message})
                },
                {
                    "contentType": "PlainText",
                    "content": formatted_message
                }
            ]
        }
    except Exception as e:
        # Registro detalhado do erro para facilitar o diagnóstico
        error_message = f"Ocorreu um erro no processamento: {str(e)}"
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Failed"
                },
                "sessionAttributes": event.get('sessionAttributes', {})
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": error_message
                }
            ]
        }
