import boto3
import datetime
from services.rekogntion_service import detect_pet_in_image
from services.s3_service import upload_from_url_to_s3

def process_request_media(mediaType, mediaUrl, user_msg):
    """
    Process the request media and return the media content.

    Args:
        mediaType (str): Type of the media.
        mediaUrl (str): Media URL.
        user_msg (str): User message.

    Returns:
        str: Media content.
    """
    
    if mediaType == 'image/jpg' or mediaType == 'image/jpeg' or mediaType == 'image/png':
        image_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "pet_image.jpg"
        # download the image from the URL and upload it to S3
        path_image = upload_from_url_to_s3(mediaUrl, image_name)
        # detect the pet in the image
        pet_detected = detect_pet_in_image(path_image)

        # get the breeds of the pets detected
        type_pet = [pet['type'] for pet in pet_detected['pets'] if 'type' in pet]
        confidence_pet = [pet['confidence'] for pet in pet_detected['pets'] if 'confidence' in pet]

        breeds = [pet['breeds'] for pet in pet_detected['pets'] if 'breeds' in pet]
        breeds_flat = [breed for sublist in breeds for breed in sublist]  
        breeds_str = ', '.join(breeds_flat)

        return f"Tipo Detectado:{type_pet[0]}, Raças detectadas: {breeds_str}, chance de acerto: {confidence_pet[0]}"

    if mediaType == 'audio/ogg':
        return "Ainda não sei processar áudios, mas estou aprendendo!"
    
    if mediaType == ['']:
        return user_msg
    
    else:
        return user_msg
