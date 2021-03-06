"""File to get the secret and parameter from AWS Secrets Manager. Is extended from the sample stub from Secrets Manager Console."""

# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/

import boto3
import base64
from botocore.exceptions import ClientError
import json


def get(secret_name, parameter_name, region_name="us-east-1"):
    boto_session = boto3.session.Session()
    return _get_secret(boto_session, secret_name, region_name), _get_parameter(boto_session, parameter_name, region_name)


def _get_secret(boto_session, secret_name, region_name="us-east-1"):
    # Create a Secrets Manager client
    client = boto_session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])


def _get_parameter(boto_session, parameter_name, region_name="us-east-1"):
    # Create a SSM client
    client = boto_session.client(
        service_name='ssm',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
    except ClientError as e:
            raise e
    else:
        return json.loads(get_secret_value_response.get("Parameter").get("Value"))
