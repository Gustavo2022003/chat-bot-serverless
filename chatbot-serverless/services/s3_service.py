import boto3
import requests
from requests.auth import HTTPBasicAuth
import os

S3_BUCKET = os.getenv('S3_BUCKET_NAME')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

s3 = boto3.client('s3')

def get_image(file_name, expiration=3600):
    """
    Generates a pre-signed URL to access an object stored in S3.

    Args:
        file_name (str): The name of the file in the S3 bucket.
        expiration (int): Expiration time for the pre-signed URL in seconds (default: 3600).

    Returns:
        str: The pre-signed URL for the file in S3.
        None: If an error occurs during the URL generation process.
    """
    if not S3_BUCKET:
        print("Erro: O nome do bucket S3 não foi configurado. Verifique a variável de ambiente 'S3_BUCKET_NAME'.")
        return None

    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': file_name
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Erro ao gerar URL para o arquivo '{file_name}' no bucket '{S3_BUCKET}': {e}")
        return None

def upload_from_url_to_s3(url, object_name, prefix="assets/"):
    """
    Faz download de um arquivo de uma URL e faz upload diretamente para o S3.

    :param url: URL do arquivo para download.
    :param object_name: Nome do arquivo no S3.
    :param prefix: Prefixo padrão para o caminho no bucket (default: 'assets/').
    """
    try:
        object_full_name = f"{prefix}{object_name}"
        # opening the stream of the URL
        with requests.get(url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), stream=True) as response:
            response.raise_for_status()  # Verifica erros no request

            # direct upload to S3
            s3.upload_fileobj(response.raw, S3_BUCKET, object_full_name)
            
            #return the full path of the object in the bucket
            return object_full_name

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL: {e}")
    except Exception as e:
        print(f"Erro ao fazer upload: {e}")
