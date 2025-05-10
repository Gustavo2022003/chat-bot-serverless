import boto3
import json
import os
from services.s3_service import get_image

rekognition = boto3.client('rekognition')
S3_BUCKET = os.getenv('S3_BUCKET_NAME')

def detect_pet_in_image(image_name):
    try:
        if not image_name:
            return {
                'success': False,
                'message': 'Nome da imagem não fornecido'
            }

        # Detecção padrão de labels
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': S3_BUCKET,
                    'Name': image_name
                }
            },
            MaxLabels=100,
            MinConfidence=70
        )

        if not response or 'Labels' not in response:
            return {
                'success': False,
                'message': 'Nenhum animal detectado na imagem'
            }

        # Mapeamento de raças de cachorro
        dog_breeds = {
            'Dalmata': ['Dalmatian'],
            'Salsicha': ['Dachshund', 'Sausage Dog', 'Wiener Dog'],
            'Pastor Alemão': ['German Shepherd', 'Shepherd Dog'],
            'Labrador': ['Labrador Retriever', 'Lab'],
            'Poodle': ['Toy Poodle', 'Standard Poodle', 'Poodle'],
            'Golden': ['Golden Retriever'],
            'Bulldog': ['French Bulldog', 'English Bulldog', 'Bulldog'],
            'Rottweiler': ['Rottweiler', 'Rott'],
            'Husky': ['Siberian Husky', 'Husky'],
            'Pug': ['Pug Dog', 'Pug'],
            'Pitbull': ['Pit Bull', 'American Pit Bull', 'Pitbull'],
            'Yorkshire': ['Yorkshire Terrier', 'Yorkie'],
            'Chihuahua': ['Chihuahua Dog', 'Chihuahua'],
            'Shih Tzu': ['Shih-Tzu', 'Shih Tzu']
        }

        # Verifica se é um cachorro
        is_dog = any(label['Name'] in ['Dog', 'Canine'] for label in response['Labels'])
        if not is_dog:
            return {
                'success': False,
                'message': 'Nenhum cachorro detectado na imagem'
            }

        # Função para verificar raça
        def check_breed(name):
            name_lower = name.lower()
            for breed, variations in dog_breeds.items():
                if any(var.lower() in name_lower for var in variations):
                    return breed
            return None

        # Procura a raça em todas as labels e seus metadados
        detected_breed = 'Não identificada'
        for label in response['Labels']:
            # Verifica a própria label
            breed = check_breed(label['Name'])
            if breed:
                detected_breed = breed
                break
            
            # Verifica nos parents
            for parent in label.get('Parents', []):
                breed = check_breed(parent['Name'])
                if breed:
                    detected_breed = breed
                    break

        # Encontra a confiança da detecção do cachorro
        dog_confidence = next(
            (label['Confidence'] for label in response['Labels'] 
                if label['Name'] in ['Dog', 'Canine']),
            0
        )

        return {
            'success': True,
            'pets': [{
                'type': 'Cachorro',
                'confidence': dog_confidence,
                'breeds': [detected_breed]
            }],
            'debug_info': {
                'total_labels': len(response['Labels']),
                'labels_names': [label['Name'] for label in response['Labels']]
            }
        }

    except Exception as e:
        print(f"Erro: {str(e)}")
        return {
            'success': False,
            'message': f'Erro ao processar imagem: {str(e)}'
        }