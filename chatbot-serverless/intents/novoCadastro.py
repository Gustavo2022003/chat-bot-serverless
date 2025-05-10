from services.dynamo.user import search_by_phone, insert_user
from utils.lex_utils import generate_lex_response

def novoCadastro(sessionState, sessionAttributes, slots, intentName):
    """
    Realiza o cadastro de um novo usuário com base nos dados fornecidos via slots.

    Verifica se o telefone já está cadastrado e, caso contrário, insere o novo usuário na base de dados.

    Args:
        sessionState (dict): O estado atual da sessão.
        sessionAttributes (dict): Atributos da sessão, utilizados para manter o contexto.
        slots (dict): Os slots da intenção, que contêm as informações fornecidas pelo usuário.
        intentName (str): O nome da intenção que está sendo executada.

    Returns:
        dict: Resposta estruturada para o Amazon Lex com a mensagem de sucesso ou erro.
    """
    # Extrai os valores dos slots com valores padrão
    name = slots.get('nome', {}).get('value', {}).get('interpretedValue', "Não informado")
    email = slots.get('e-mail', {}).get('value', {}).get('interpretedValue', "Não informado")
    phone = slots.get('telefone', {}).get('value', {}).get('interpretedValue', "Não informado")
    age = slots.get('idade', {}).get('value', {}).get('interpretedValue', "Não informado")

    try:
        # Verifica se o telefone já está cadastrado
        result = search_by_phone(phone)

        if not result:
            # Insere o novo usuário no banco de dados
            user = insert_user(name, email, phone, age)
            print(user)  # Para debug

            # Atualiza os atributos da sessão com os dados do novo usuário
            sessionAttributes['nome'] = name
            sessionAttributes['e-mail'] = email
            sessionAttributes['telefone'] = phone
            sessionAttributes['idade'] = age
            sessionAttributes['userId'] = user.get('id')

            # Mensagem de sucesso
            response_message = "Novo cadastro realizado com sucesso."
        else:
            # Caso o telefone já esteja cadastrado
            response_message = "O telefone já está cadastrado."

        # Retorna a resposta para o Amazon Lex
        return generate_lex_response(
            intentName=intentName,
            sessionState=sessionState,
            sessionAttributes=sessionAttributes,
            message=response_message,
            state="Fulfilled",
            showOptions=True
        )

    except Exception as e:
        # Captura erros de exceção e retorna uma resposta de erro
        error_message = f"Ocorreu um erro ao realizar o cadastro: {str(e)}"
        print(error_message)  # Para debug
        
        # Retorna uma resposta indicando falha
        return generate_lex_response(
            intentName=intentName,
            sessionState=sessionState,
            sessionAttributes=sessionAttributes,
            message=error_message,
            state="Failed",
            showOptions=False
        )
