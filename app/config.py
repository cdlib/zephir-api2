import os
import json

import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name):
    client = boto3.client("secretsmanager")

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)


def get_database_uri():
    database_uri = os.getenv("DATABASE_URI")
    if database_uri:
        return database_uri
    
    db_credentials_secret_name = os.getenv("DATABASE_CREDENTIALS_SECRET_NAME")
    if db_credentials_secret_name:
        secret = get_secret(db_credentials_secret_name)
        db_username = secret["username"]
        db_password = secret["password"]
        db_host = secret["host"]
        db_database = secret["dbname"]
    else:
        db_username = os.getenv("DB_USERNAME")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_database = os.getenv("DB_DATABASE")

    return f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_database}?charset=utf8mb4"


class Config:
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL")
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False