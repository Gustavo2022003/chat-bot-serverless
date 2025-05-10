import boto3
import hashlib
import os
import json

def text_to_speech(text):
    try:
        polly = boto3.client('polly')
        s3 = boto3.client('s3')
        bucket_name = os.environ['BUCKET_NAME']
        
        # create a unique file name
        file_name = hashlib.md5(text.encode()).hexdigest() + '.mp3'
        
        # synthesizes the text into speech
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Vitoria'  # Voz bem robotico considerar mudar e olhar os valores das vozes neurais
        )
        
        # upload the file to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=response['AudioStream'].read(),
            ContentType='audio/mpeg'
        )
        
        # generate the URL of the file
        url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        
        return url
    except Exception as e:
        print(f"Error: {e}")
        return None