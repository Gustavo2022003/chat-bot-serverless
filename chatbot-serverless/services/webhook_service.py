import boto3
import os
import json
import logging
import time
from urllib.parse import parse_qs, urlencode
from twilio.twiml.messaging_response import MessagingResponse
from services.dynamo.lex_sessions import get_session, save_session
from utils.webhook_utils import process_request_media

# log config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# lex v2 client
lex_v2_client = boto3.client('lexv2-runtime')

# Config vars lex v2
BOT_ID = os.getenv('BOT_ID')
BOT_ALIAS_ID = os.getenv('BOT_ALIAS_ID')
LOCALE_ID = 'pt_BR'

def webhook_service(event, context):
    """Handler principal do webhook."""
    try:
        body = event.get('body', '')
        if isinstance(body, (bytes, bytearray)):
            body = body.decode('utf-8')  # decode the request body

        # decode to application/x-www-form-urlencoded format
        params = parse_qs(body)

        user_msg = params.get('Body', [''])[0]  # user's message
        user_id = params.get('From', [''])[0]   # user's phone number
        mediaType = params.get('MediaContentType0', [''])[0]  # media type
        mediaUrl = params.get('MediaUrl0', [''])[0]  # media URL
        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Entrada inválida: falta Body ou From"})
            }

        user_id = user_id.replace('whatsapp:+', '')  # remove the prefix from the phone number
        print(f"Requisição decodificada {params}")
        request_msg_processed = process_request_media(mediaType, mediaUrl, user_msg)
        print (f"Request Processed: {request_msg_processed}")

        


        # get session from DynamoDB
        session_attributes = get_session(user_id)
        if not session_attributes:
            session_attributes = {}
        print("Session Attributes: ", session_attributes)
        print("Antes do Lex")
        # using Lex V2 to recognize the text
        resposta_lex = lex_v2_client.recognize_text(
            botId=BOT_ID,
            botAliasId=BOT_ALIAS_ID,
            localeId=LOCALE_ID,
            sessionId=user_id,
            text=request_msg_processed,
            sessionState={
                'sessionAttributes': session_attributes
            }
        )

        # Update session with new attributes
        session_updated = resposta_lex.get('sessionState', {})
        new_session_attributes = session_updated.get('sessionAttributes', {})

        # save session at dynamo
        save_session(user_id, new_session_attributes)

        # extract messages from Lex response
        bot_msg = resposta_lex.get('messages', [])

        twilio_response = MessagingResponse()

        for msg in bot_msg:
            if 'content' in msg:
                content = msg['content']
                try:
                    # convert the content to a dictionary
                    content_dict = json.loads(content)
                    if 'image' in content_dict:
                        print(f"Imagem: {content_dict['image']}")
                        twilio_response.message().media(content_dict['image'])
                    if 'audio' in content_dict:
                        print(f"Audio: {content_dict['audio']}")
                        twilio_response.message().media(content_dict['audio'])
                    if 'text' in content_dict:
                        print(f"Texto: {content_dict['text']}")
                        twilio_response.message(content_dict['text'])
                    
                except (json.JSONDecodeError, TypeError):
                    # Se a conversão falhar, tratar como string
                    print(f"Texto: {content}")
                    twilio_response.message(content)

            

        print(f"Resposta TwiML: {twilio_response}")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/xml"  # Especificar que a resposta é em XML
            },
            "body": str(twilio_response)  # Converter a resposta TwiML para string
        }
        

    except Exception as e:
        logger.error(f"Erro ao processar a requisição: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Erro interno no servidor: {str(e)}"})
        }