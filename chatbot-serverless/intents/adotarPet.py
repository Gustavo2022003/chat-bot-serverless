import json
from services.dynamo.pets import get_pets
from services.dynamo.adopt_solicitations import insert_adopt_solicitation
from utils.lex_utils import animal_exists
from services.polly_service import text_to_speech

def adotarPet(event):
    """
    Gerencia o processo de adoção de um animal em um bot de atendimento.

    Esta função é chamada ao ativar a intenção "adotarPet". Ela valida as informações fornecidas pelo usuário,
    verifica a disponibilidade do animal escolhido no banco de dados, e realiza as etapas para registrar a
    solicitação de adoção.

    Args:
        event (dict): Um dicionário contendo os dados do evento, que inclui o estado da sessão,
        slots capturados pelo bot, e outros atributos da sessão.

    Estrutura esperada do `event`:
        - sessionState (dict):
            - intent (dict):
                - name (str): Nome da intenção.
                - slots (dict): Slots capturados pelo bot, contendo valores interpretados.
            - sessionAttributes (dict, opcional): Atributos da sessão como userId e telefone.
        - outros campos podem ser ignorados pela função.

    Comportamento:
        1. Verifica se o usuário escolheu um animal no slot "AnimalToAdopt".
        2. Valida a existência do animal escolhido no banco de dados usando a função `animal_exists`.
        3. Se o animal existir:
            - Obtém os atributos da sessão, como userId e telefone.
            - Registra a solicitação de adoção com a função `insert_adopt_solicitation`.
            - Retorna uma mensagem confirmando ou indicando um erro no registro.
        4. Se o animal escolhido não estiver disponível, solicita que o usuário escolha novamente
            a partir de uma lista de opções.
        5. Se nenhum animal estiver disponível, retorna uma mensagem informando a indisponibilidade.

    Retorna:
        dict: Uma resposta formatada para o bot, que pode ser uma mensagem finalizada, um pedido
        de entrada adicional do usuário (elicit slot), ou uma confirmação de sucesso/erro.

    Dependências:
        - `animal_exists(animal_chosen)`: Função que verifica a existência de um animal no banco de dados.
        - `insert_adopt_solicitation(pet_id, phone, user_id)`: Função que registra a solicitação de adoção.
        - `show_pets_list()`: Função que retorna uma lista de animais disponíveis para adoção.
        - `close_dialog(sessionAttributes, intent_name, message, slots)`: Retorna uma mensagem de diálogo finalizado.
        - `elicit_slot_with_list(session_attributes, intent_name, slot_to_elicit, message, options)`: Solicita um slot específico ao usuário, com uma lista de opções.

    Exemplo:
        event = {
            "sessionState": {
                "intent": {
                    "name": "adotarPet",
                    "slots": {
                        "AnimalToAdopt": {"value": {"interpretedValue": "Cachorro - Labrador"}}
                    }
                },
                "sessionAttributes": {"userId": "12345", "phone": "555-1234"}
            }
        }

        resposta = adotarPet(event)
    """
    intent_name = event['sessionState']['intent']['name']
    slots = event['sessionState']['intent']['slots']
    slot_name = "AnimalToAdopt"
    sessionAttributes = event['sessionState'].get('sessionAttributes', {})

    if intent_name == "adotarPet":
        # verify if the user has chosen an animal
        if slots.get(slot_name) and slots[slot_name].get('value'):
            animal_chosen = slots[slot_name]['value']['interpretedValue']
            # validate if the animal exists in the database
            pet = animal_exists(animal_chosen)
            print("Pet na intent adotarPet", pet) 
            if pet:
                print(sessionAttributes)
                pet_id = pet.get('id')
                user_id = sessionAttributes.get('userId')
                phone = sessionAttributes.get('phone')

                if insert_adopt_solicitation(pet_id, phone, user_id) is None:
                    return close_dialog(
                        sessionAttributes,
                        intent_name,
                        "Desculpe, ocorreu um erro ao tentar adotar o animal. Por favor, tente novamente.",
                        slots
                    )
                else:
                    return close_dialog(
                        sessionAttributes,
                        intent_name,
                        f"Sua solicitação para adotar o Cachorro '{pet['nome']}' foi recebida. Em breve entraremos em contato.",
                        slots
                    )
            else:
                # return a message if the animal chosen is not available
                return elicit_slot_with_list(
                    session_attributes=sessionAttributes,
                    intent_name=intent_name,
                    slot_to_elicit=slot_name,
                    message="O animal escolhido não está disponível. Por favor, escolha da lista abaixo:",
                    options=show_pets_list()
                )

        # search for available pets in the database
        animal_options = show_pets_list()

        # return a message if there are no animals available
        if not animal_options:
            return close_dialog(
                intent_name,
                "Desculpe, não temos animais disponíveis no momento.",
                slots
            )

        # return the list of available pets to the user
        return elicit_slot_with_list(
            session_attributes=sessionAttributes,
            intent_name=intent_name,
            slot_to_elicit=slot_name,
            message="Aqui estão os animais disponíveis para adoção. Qual você prefere? Digite a resposta no seguinte formato (Nome - Raça)",
            options=animal_options
        )


def show_pets_list():
    """
    Retorna uma lista de animais disponíveis para adoção.

    Esta função consulta o banco de dados de animais disponíveis, formata as informações relevantes 
    em uma lista de strings, e filtra somente os animais que estão marcados como "disponíveis".

    Retorna:
        list: Uma lista de strings, onde cada string contém as informações de um animal disponível no formato:
              "Nome - Espécie - Raça".
              Caso não haja animais disponíveis ou ocorra um problema na consulta, retorna uma lista vazia.

    Dependências:
        - `get_pets()`: Função que retorna uma lista de dicionários, onde cada dicionário representa
          um animal com atributos como 'nome', 'especie', 'raça' e 'disponivel'.

    Exemplo de retorno:
        [
            "Rex - Cachorro - Labrador",
            "Mimi - Gato - Siamês",
            "Bidu - Cachorro - Poodle"
        ]

    Tratamento de erros:
        - Caso `get_pets` retorne `None` ou um valor não esperado, a função garante que uma lista vazia seja retornada.
    """
    pets = get_pets()
    
    # Garante que `pets` seja uma lista válida
    if not pets or not isinstance(pets, list):
        return []

    # Formata os resultados, filtrando apenas os animais disponíveis
    formatted_pets = [
        f"{pet.get('nome', 'Unknown')} - {pet.get('especie', 'Unknown')} - {pet.get('raça', 'Unknown')}"
        for pet in pets if pet.get('disponivel', True)
    ]

    return formatted_pets

def elicit_slot_with_list(session_attributes, intent_name, slot_to_elicit, message, options):
    """
    Cria uma resposta do Amazon Lex para solicitar um slot ao usuário, apresentando uma lista de opções.

    Esta função constrói o payload de resposta com:
    - Uma mensagem de texto informativa.
    - Uma lista de opções formatada como um payload personalizado, ideal para integração com interfaces de usuário que suportam exibição de listas.

    Args:
        session_attributes (dict): Os atributos da sessão, usados para manter informações do contexto do usuário.
        intent_name (str): O nome da intenção em andamento.
        slot_to_elicit (str): O nome do slot que está sendo solicitado.
        message (str): A mensagem de texto a ser exibida ao usuário.
        options (list): Uma lista de strings representando as opções disponíveis para o usuário.

    Returns:
        dict: Um payload estruturado para o Amazon Lex, contendo:
            - Ação de diálogo configurada como "ElicitSlot".
            - Slot que será solicitado.
            - Mensagem de texto e opções formatadas para o usuário.

    Exemplo:
        session_attributes = {"userId": "12345"}
        intent_name = "adotarPet"
        slot_to_elicit = "AnimalToAdopt"
        message = "Escolha um dos seguintes animais para adoção:"
        options = ["Rex - Cachorro - Labrador", "Mimi - Gato - Siamês"]

        resposta = elicit_slot_with_list(session_attributes, intent_name, slot_to_elicit, message, options)

        Resultado:
        {
            "sessionState": {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "slotToElicit": "AnimalToAdopt"
                },
                "intent": {
                    "name": "adotarPet",
                    "slots": {}
                },
                "sessionAttributes": {"userId": "12345"}
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Escolha um dos seguintes animais para adoção:"
                },
                {
                    "contentType": "CustomPayload",
                    "content": "Rex - Cachorro - Labrador\nMimi - Gato - Siamês"
                }
            ],
        }
    """
    options_string = "\n".join(options)

    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_to_elicit
            },
            "intent": {
                "name": intent_name,
                "slots": {}
            },
            "sessionAttributes": session_attributes
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            },
            {
                "contentType": "CustomPayload",
                "content": options_string
            }
        ],
    }


def close_dialog(session_attributes, intentName, message, slots):
    """
    Finaliza o diálogo com o usuário após a conclusão da interação.

    Esta função cria o payload de resposta para o Amazon Lex quando a interação é concluída. 
    O estado da intenção é definido como "Fulfilled", e uma mensagem final é enviada ao usuário, 
    opcionalmente acompanhada de áudio gerado por texto para fala (TTS).

    Args:
        session_attributes (dict): Atributos da sessão, utilizados para manter o contexto do usuário.
        intentName (str): O nome da intenção que está sendo finalizada.
        message (str): A mensagem final que será exibida ao usuário.
        slots (dict): Um dicionário contendo os slots usados na intenção.

    Returns:
        dict: Um payload estruturado para o Amazon Lex contendo:
            - Ação de diálogo configurada como "Close".
            - Estado da intenção definido como "Fulfilled".
            - Mensagem final em texto.
            - Um payload personalizado com áudio gerado, se aplicável.

    Dependências:
        - `text_to_speech(message)`: Função que converte o texto da mensagem em áudio.

    Exemplo:
        session_attributes = {"userId": "12345"}
        intentName = "adotarPet"
        message = "Sua solicitação foi concluída com sucesso!"
        slots = {"AnimalToAdopt": {"value": {"interpretedValue": "Cachorro - Labrador"}}}

        resposta = close_dialog(session_attributes, intentName, message, slots)

        Resultado:
        {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": "adotarPet",
                    "state": "Fulfilled",
                    "slots": {
                        "AnimalToAdopt": {"value": {"interpretedValue": "Cachorro - Labrador"}}
                    }
                },
                "sessionAttributes": {"userId": "12345"}
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Sua solicitação foi concluída com sucesso!"
                },
                {
                    "contentType": "CustomPayload",
                    "content": '{"audio": "audio_url"}'
                }
            ]
        }
    """
    audio_message = text_to_speech(message)

    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intentName,
                "state": "Fulfilled",
                "slots": slots
            },
            "sessionAttributes": session_attributes
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            },
            {
                "contentType": "CustomPayload",
                "content": json.dumps({"audio": audio_message})
            }
        ]
    }
