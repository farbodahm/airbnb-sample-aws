""" Migrate Airbnb CSVs to DB uploaded to S3. """
import boto3
import csv
import json
from os import environ
import pymysql

s3 = boto3.resource('s3')

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
    )
except pymysql.MySQLError as e:
    print('ERROR: Unexpected error: Could not connect to MySQL instance.')
    print(e)
    raise


def write_listings_csv_to_db(bucket_name: str, object_key: str) -> None:
    """ Write Listings CSV uploaded file to DB """
    s3_object = s3.Object(bucket_name, object_key)
    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()

    lines = csv.reader(data)
    
    next(lines)  # Skip CSV headers

    data = [(line[0], line[1], line[5], line[6], line[7], line[8], line[9],) for line in lines]
    query = "INSERT INTO listings (`id`, `name`, `neighbourhood`, `latitude`, `longitude`, `room_type`, `price`)\
             VALUES (%s, %s, %s, %s, %s, %s, %s)"

    with conn.cursor() as cur:
        try:
            result = cur.executemany(query, data)
        except Exception as e:
            print('Unexpected error: could not write data to db:\n', e)

    conn.commit()
    print(f'Item Count: {result}')


def write_calendars_csv_to_db(bucket_name: str, object_key: str) -> None:
    """ Write Calendars CSV uploaded file to DB """
    s3_object = s3.Object(bucket_name, object_key)
    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()

    lines = csv.reader(data)
    
    next(lines)  # Skip CSV headers

    data = [(line[0], line[1], line[2], line[3][1:], line[5], line[6],) for line in lines]
    query = "INSERT INTO calendars (`listing_id`, `start_date`, `available`, `price`, `minimum_nights`, `maximum_nights`)\
             VALUES (%s, %s, %s, %s, %s, %s)"

    with conn.cursor() as cur:
        try:
            result = cur.executemany(query, data)
        except Exception as e:
            print('Unexpected error: could not write data to db:\n', e)

    conn.commit()
    print(f'Item Count: {result}')


def handler(event: dict, context):
    """ Handler func is called when a new file is uploaded to S3 bucket """
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        if 'listings' in object_key:
            write_listings_csv_to_db(bucket_name, object_key)
        elif 'calendar' in object_key:
            write_calendars_csv_to_db(bucket_name, object_key)
