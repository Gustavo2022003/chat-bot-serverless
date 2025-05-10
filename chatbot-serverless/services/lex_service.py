
from utils.lex_utils import generate_lex_response
from intents.verificacaoCadastro import verifcacaoCadastro
from intents.novoCadastro import novoCadastro
from intents.adotarPet import adotarPet
from intents.doacaoOng import doacaoOng
from intents.identificarCachorro import identificarCachorro

def lex_response(intentName, event):
    try:
        # call the function that corresponds to the intent
        response = select_intent(intentName, event)
        return response
    except Exception as e:
        # return an error message if an exception occurs
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


def select_intent(intentName, event):
    # get session attributes, state, intent and slots from event
    sessionAttributes = event.get('sessionAttributes', {})
    sessionState = event.get('sessionState', {})
    intent = sessionState.get('intent', {})
    slots = intent.get('slots', {})

    # redirects to the "verificacaoCadastro" intent
    if intentName == "verificacaoCadastro":
        return verifcacaoCadastro(sessionState, sessionAttributes, slots, intentName)

    # redirects to the "novoCadastro" intent
    if intentName == "novoCadastro":
        return novoCadastro(sessionState, sessionAttributes, slots, intentName)
    
    # redirects to the "adotarPet" intent
    if intentName == "adotarPet":
        return adotarPet(event)
    
    # redirects to the "doacaoOng" intent
    if intentName == "doacaoOng":
        return doacaoOng(event)
    
    if intentName == "IdentificarCachorro":
        return identificarCachorro(event)

    # if the intent is not recognized, return a message to the user
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Failed"
            },
            "sessionAttributes": sessionAttributes
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": "Intent não reconhecido."
            }
        ]
    }
