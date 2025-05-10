import os
import json
from services.s3_service import get_image
from services.polly_service import text_to_speech

S3_BUCKET = os.getenv('S3_BUCKET_NAME')

def doacaoOng(event):
    """
    Processa a intenção de doação para a ONG, fornecendo um QR Code de PIX e mensagens de agradecimento.

    Args:
        event (dict): O evento recebido, contendo o estado da sessão e outras informações do Lex.

    Retorna:
        dict: Payload estruturado para o Amazon Lex, incluindo a imagem do QR Code,
        uma mensagem de agradecimento, e áudio gerado por texto para fala.
    """
    try:
        # Obtém informações da intenção e atributos da sessão
        intent_name = event['sessionState']['intent']['name']
        session_attributes = event['sessionState'].get('sessionAttributes', {})

        # URL da imagem do QR Code armazenada no S3
        pix_image_url = f'https://{S3_BUCKET}.s3.amazonaws.com/images/Projeto_Compass.png'

        # Mensagem formatada para texto e áudio
        formatted_message = (
            "Você pode realizar sua doação para a ONG através do QRCODE de PIX acima! <3 \n"
            "Agradecemos sua iniciativa para a doação, qualquer valor será bem-vindo! \n\n"
        )
        audio_message = text_to_speech(formatted_message)

        # Conteúdo da imagem para payload customizado
        json_image = {"image": pix_image_url}

        # Retorno estruturado para encerrar o diálogo
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
                    "content": json.dumps(json_image)
                },
                {
                    "contentType": "CustomPayload",
                    "content": json.dumps({"audio": audio_message})
                },
                {
                    "contentType": "PlainText",  # Usar PlainText para mensagens que não requerem parsing
                    "content": formatted_message
                }
            ]
        }
    except Exception as e:
        # Tratamento de erro para capturar falhas e informar o usuário
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
                    "content": f"Ocorreu um erro no processamento: {str(e)}"
                }
            ]
        }
