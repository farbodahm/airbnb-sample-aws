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
    headers = next(lines)

    item_count = 0
    with conn.cursor() as cur:
        for line in lines:
            query = f"INSERT INTO listings (`id`, `name`, `neighbourhood`, `latitude`, `longitude`, `room_type`, `price`)\
                      VALUES ('{line[0]}', '{line[1]}', '{line[5]}', '{line[6]}', '{line[7]}', '{line[8]}', '{line[9]}')"
            try:
                cur.execute(query)
            except Exception as e:
                print(line, query)
                print(e)
            else:
                item_count += 1

    conn.commit()
    print(f'Item Count: {item_count}')

def handler(event: dict, context):
    for record in event['Records']:                  
        bucket_name = record['s3']['bucket']['name']         
        object_key = record['s3']['object']['key']
        write_listings_csv_to_db(bucket_name, object_key) 
