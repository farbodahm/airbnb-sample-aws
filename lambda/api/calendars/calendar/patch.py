""" Respond to GET /calendars """
from typing import List, Tuple
import pymysql
import boto3
import json
from os import environ


# Get DB credentails from SecretsManager
secrets_manager = boto3.client('secretsmanager')
secret_value = secrets_manager.get_secret_value(
    SecretId=environ['DB_SECRET_MANAGER_ARN']
)
database_secrets = json.loads(secret_value['SecretString'])


# Connect to DB
try:
    conn = pymysql.connect(
        host=database_secrets['host'],
        user=database_secrets['username'],
        passwd=database_secrets['password'],
        db=database_secrets['dbname'],
        cursorclass=pymysql.cursors.DictCursor,
    )
except pymysql.MySQLError as e:
    print("ERROR: Unexpected error: Could not connect to MySQL instance.")
    print(e)
    raise


def update_calendars_availability(calendar_id: str,
                                  availability: str) -> int:
    """
    Update calendar_id's availability in DB
    Returns:
        int: Succeeded or not
    """

    query = """
    UPDATE calendars
    SET
        available = %s
    WHERE
        (calendar_id = %s)
    """

    with conn.cursor() as cur:
        try:
            result_count = cur.execute(
                query,
                (availability,
                 calendar_id,)
            )
        except Exception as e:
            print('Unexpected error: could not write data to db:\n', e)

    conn.commit()
    return result_count


def handler(event: dict, context):
    """ Respond to the API Gateway request """
    body = json.loads(event['body'])
    result_count = update_calendars_availability(
        event['pathParameters']['calendar_id'],
        body['available'],
    )
    status_code = 200
    result = {
        "msg": "Room booked successfully."
    }

    # If couldn't book the room
    if result_count == 0:
        status_code = 400
        result = {
            "msg": "Couldn't book the room."
        }

    response = {
        "itemCount": result_count,
        "data": result
    }

    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {},
        "multiValueHeaders": {},
        "body": json.dumps(response, default=str,)
    }
