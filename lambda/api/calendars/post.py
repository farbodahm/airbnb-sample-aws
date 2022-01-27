""" Respond to POST /calendars """
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


def process_new_calendars(event: dict) -> List[Tuple]:
    """
    Prepare the incoming data for inserting into DB 
    Returns:
        List[Tuple]: List of given data converted to DB format tuples
    """
    new_calendars: List[Tuple] = []

    for record in event['Records']:
        body = json.loads(record['body'])
        new_calendars.append(
            (
                body['listing_id'],
                body['start_date'],
                body['available'],
                body['price'],
                body['minimum_nights'],
                body['maximum_nights'],
            )
        )

    return new_calendars


def add_new_calendars_to_db(new_calendars: List[Tuple]) -> int:
    """
    Insert new calendars to DB.
    Returns:
        int: Number of inserted rows.
    """

    query = """
    INSERT INTO calendars (listing_id, start_date, available, price, minimum_nights, maximum_nights)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    with conn.cursor() as cur:
        try:
            result_count = cur.executemany(
                query,
                new_calendars,
            )
        except Exception as e:
            print('Unexpected error: could not write data to db:\n', e)

    conn.commit()
    return result_count


def handler(event: dict, context):
    result = add_new_calendars_to_db(
        process_new_calendars(event)
    )
    print(f'Inserted {result} new calendars requests.')

    body = {
        "result": result
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
