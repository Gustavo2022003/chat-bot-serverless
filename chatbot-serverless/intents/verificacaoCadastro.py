from services.dynamo.user import search_by_phone, insert_user
from utils.lex_utils import generate_lex_response

def verifcacaoCadastro(sessionState, sessionAttributes, slots, intentName):
    """
    Verifica o cadastro de um usuário com base no telefone fornecido e retorna as informações do cadastro,
    caso encontrado.

    Args:
        sessionState (dict): O estado atual da sessão.
        sessionAttributes (dict): Atributos da sessão, utilizados para manter o contexto.
        slots (dict): Os slots da intenção, que contêm as informações fornecidas pelo usuário.
        intentName (str): O nome da intenção que está sendo executada.

    Returns:
        dict: Resposta estruturada para o Amazon Lex com a mensagem de sucesso ou erro.
    """
    phone = slots.get('verificaTelefone', {}).get('value', {}).get('interpretedValue', "Não informado")

    # Valida se o telefone foi informado
    if phone == "Não informado":
        response_message = "Por favor, forneça um telefone para verificar seu cadastro."
        return generate_lex_response(
            intentName=intentName,
            sessionState=sessionState,
            sessionAttributes=sessionAttributes,
            message=response_message,
            state="Failed",
            showOptions=False
        )

    try:
        # Busca o usuário no banco de dados com base no telefone
        result = search_by_phone(phone)

        if result:
            # Caso encontre o cadastro, pega o primeiro usuário encontrado
            user = result[0]
            
            # Atualiza os slots com as informações do usuário
            slots.update({
                'nome': {"value": {"interpretedValue": user.get('name', "Desconhecido")}},
                'e-mail': {"value": {"interpretedValue": user.get('email', "Desconhecido")}},
                'telefone': {"value": {"interpretedValue": user.get('phone', "Desconhecido")}},
                'idade': {"value": {"interpretedValue": user.get('age', "Desconhecido")}}
            })

            # Atualiza os atributos da sessão
            sessionAttributes.update({
                'nome': user.get('name'),
                'e-mail': user.get('email'),
                'telefone': user.get('phone'),
                'idade': user.get('age'),
                'userId': user.get('id')
            })

            # Atualiza os slots no sessionState
            sessionState['intent']['slots'] = slots

            # Mensagem de sucesso
            response_message = "Cadastro encontrado com sucesso."

        else:
            # Caso o cadastro não seja encontrado
            response_message = "Cadastro não encontrado. Digite 'Recomeçar' para reiniciar a conversa!"

    except Exception as e:
        # Caso ocorra uma falha ao acessar o banco ou outros erros
        response_message = f"Ocorreu um erro ao tentar verificar seu cadastro: {str(e)}"
        print(f"Erro de verificação: {str(e)}")  # Para debug

    return generate_lex_response(
        intentName=intentName,
        sessionState=sessionState,
        sessionAttributes=sessionAttributes,
        message=response_message,
        state="Fulfilled" if result else "Failed",
        showOptions=True
    )
