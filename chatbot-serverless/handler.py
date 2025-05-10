import json
from services.lex_service import lex_response
from services.polly_service import text_to_speech
from services.dynamo.pets import get_pets, insert_pet
from services.dynamo.adopt_solicitations import get_adopt_solicitations
from services.rekogntion_service import detect_pet_in_image
from services.webhook_service import webhook_service

def handler_geral(event, context):
    """
    Main handler for a basic API.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: Response with HTTP status 200 and a simple message.
    """
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello World!",
        }),
    }
    return response

def lex_handler(event, context):
    """
    Handler for integration with Amazon Lex.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: Response processed by the Lex service.
    """
    intentName = event['sessionState']['intent']['name']
    response = lex_response(intentName, event)
    return response

def polly_handler(event, context):
    """
    Handler for text-to-speech conversion using Amazon Polly.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: HTTP response containing the result of text-to-speech processing.
    """
    try:
        body = json.loads(event['body'])
        text = body.get('text')
        
        if not text:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Text parameter is required"})
            }
        
        return text_to_speech(text)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def apiGetPets(event, context):
    """
    Handler to retrieve the list of registered pets.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: HTTP response with the list of pets or an error message.
    """
    try:
        response_pets = get_pets()
        print(response_pets)
        
        if response_pets is None:
            response = {
                "statusCode": 404,
                "body": json.dumps({
                    "message": "No pets found",
                }),
            }
        else:       
            response = {
                "statusCode": 200,
                "body": json.dumps(response_pets),
            }
        
        return response
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def apiPostPets(event, context):
    """
    Handler to register a new pet.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: HTTP response indicating success or failure when registering the pet.
    """
    try:
        body = json.loads(event['body'])
        name = body.get('nome', '').strip()
        specie = body.get('especie', '').strip()
        breed = body.get('raça', 'Sem raça específica').strip()
        age = body.get('idade')

        if not name or not specie or not age:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "All fields are required: name, species, and age"})
            }
        
        if not isinstance(name, str) or len(name) > 100:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The 'name' field must be a string with up to 100 characters"})
            }
        
        if specie not in ['Cachorro', 'Gato', 'Pássaro']:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The 'species' field must be 'Cachorro', 'Gato', or 'Pássaro'"})
            }
        
        if not isinstance(age, (int, float)) or age <= 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The 'age' field must be a positive number"})
            }

        valid_breeds = {
            'Cachorro': ['Labrador', 'Poodle', 'Beagle', 'Sem raça específica'],
            'Gato': ['Siamês', 'Persa', 'Maine Coon', 'Sem raça específica'],
            'Pássaro': ['Canário', 'Papagaio', 'Calopsita', 'Sem raça específica']
        }

        if breed not in valid_breeds.get(specie, []):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid breed for species '{specie}'"})
            }

        if insert_pet(name, specie, breed, age):
            return {
                "statusCode": 201,
                "body": json.dumps({"message": "Pet successfully created"}),
            }

        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error saving the pet to the database"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def apiGetAdoptSolicitations(event, context):
    """
    Handler to retrieve adoption solicitations.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: HTTP response with the adoption solicitations or an error message.
    """
    try:
        response_solicitations = get_adopt_solicitations()

        if not response_solicitations:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "success": False,
                    "message": "No adoption solicitations found",
                    "data": [],
                }),
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": "Adoption solicitations found",
                "data": response_solicitations,
                "count": len(response_solicitations),
            }),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
    

def webhook_handler(event, context):
    """
    Handler for a webhook that receives a POST request.

    Args:
        event (dict): Event data received by the Lambda function.
        context (object): Context of the Lambda execution.

    Returns:
        dict: HTTP response with the body of the request.
    """

    return webhook_service(event, context)

def apiDetectPet(event, context):
    """
    Handler para detectar pets em imagens do S3.
    """
    try:
        if not event.get('body'):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Body da requisição está vazio"})
            }

        body = json.loads(event['body'])
        image_name = body.get('image_name')

        if not image_name:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "O nome da imagem é obrigatório"})
            }

        result = detect_pet_in_image(image_name)
        
        return {
            "statusCode": 200 if result['success'] else 400,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }