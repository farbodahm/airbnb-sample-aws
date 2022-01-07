""" Initialize Database during update or creation. """
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
print("Trying to connect...")
try:
    conn = pymysql.connect(
        host=database_secrets['host'],
        user=database_secrets['username'],
        passwd=database_secrets['password'],
        db=database_secrets['dbname'],
    )
except pymysql.MySQLError as e:
    print("ERROR: Unexpected error: Could not connect to MySQL instance.")
    print(e)
    raise

# TODO: Put queries in seperate .sql file
queries = [
    """CREATE TABLE IF NOT EXISTS listings (
id INT PRIMARY KEY, 
name VARCHAR(90), 
neighbourhood VARCHAR(65),
latitude DOUBLE,
longitude DOUBLE,
room_type VARCHAR(25),
price INT)""",
]


def handler(event: dict, context):
    """ Create DB tables during deployment """
    item_count = 0

    with conn.cursor() as cur:
        for query in queries:
            cur.execute(query)
            item_count += 1

        conn.commit()

    conn.commit()
    return {'status': 'ok', 'item_count': item_count}
