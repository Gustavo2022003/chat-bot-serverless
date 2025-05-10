import boto3
import os
from datetime import datetime
import uuid

from utils.dynamo_utils import format_phone_number

TABLE_DYNAMO_USERS = os.getenv('DYNAMODB_TABLE_USERS')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_DYNAMO_USERS)

def search_by_phone(phone):
    formPhone = format_phone_number(phone)
    response = table.query(
        IndexName='PhoneIndex',
        KeyConditionExpression=boto3.dynamodb.conditions.Key('phone').eq(formPhone)
    )
    return response.get('Items', None)

def insert_user(name, email, phone, age):
    formPhone = format_phone_number(phone)

    response = table.put_item(Item={
        'id': str(uuid.uuid4()),  # Gera um UUID para o id
        'name': name,
        'email': email,
        'phone': formPhone,
        'age': age
    })
    return response

def get_user_by_id(id):
    print("ID", id)
    response = table.get_item(Key={'id': id})
    print("Response", response)
    return response.get('Item', None)



