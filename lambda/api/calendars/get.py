""" Respond to GET /calendars """
from typing import List, Tuple
import pymysql
import boto3
import json
from os import environ

DB_DEFAULT_PAGE_SIZE = 10

# Get DB credentails from SecretsManager
secrets_manager = boto3.client('secretsmanager')
secret_value = secrets_manager.get_secret_value(
    SecretId=environ['DB_SECRET_MANAGER_ARN']
)
database_secrets = json.loads(secret_value['SecretString'])


# Connect to DB
print("Trying to connect...")
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


def get_calendars_from_db(parameter_available: str,
                          parameter_date: str,
                          parameter_days: str,
                          page_number: int,
                          ) -> Tuple[int, List[dict]]:
    """
    Return the calendars from DB that have the parameters needed by the client.
    page_number (int): Is used for pagination.
    """

    query = """
    SELECT
        c.calendar_id,
        l.name,
        l.neighbourhood,
        l.latitude,
        l.longitude,
        l.room_type,
        c.start_date,
        c.minimum_nights,
        c.maximum_nights,
        c.price
    FROM
        listings l
            JOIN
        calendars c ON c.listing_id = l.id
    WHERE
        c.available = %s
            AND c.start_date = %s
            AND %s BETWEEN c.minimum_nights AND c.maximum_nights
    ORDER BY c.price
    LIMIT %s , %s
    """

    with conn.cursor() as cur:
        try:
            result_count = cur.execute(
                query,
                (parameter_available,
                 parameter_date,
                 parameter_days,
                 (page_number-1) * DB_DEFAULT_PAGE_SIZE,
                 DB_DEFAULT_PAGE_SIZE,)
            )

            result = cur.fetchall()
        except Exception as e:
            print('Unexpected error: could not write data to db:\n', e)
    
    return (result_count, result,)


def handler(event: dict, context):
    """ Respond to the API Gateway request """
    result_count, result = get_calendars_from_db(
        event['queryStringParameters']['available'],
        event['queryStringParameters']['date'],
        event['queryStringParameters']['days'],
        int(event['queryStringParameters'].get('page', 1)),
    )
    status_code = 200

    # If no calendar is found with the required parameters
    if result_count == 0:
        status_code = 404
        result = {
            "msg": "There are no rooms with your required parameters."
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
