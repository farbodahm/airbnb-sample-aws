""" Migrate Airbnb CSVs to DB uploaded to S3. """
import boto3
import csv

s3 = boto3.resource('s3')

def write_listings_csv_to_db(bucket_name: str, object_key: str) -> None:
    """ Write Listings CSV uploaded file to DB """
    s3_object = s3.Object(bucket_name, object_key)
    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()

    lines = csv.reader(data)
    headers = next(lines)
    for line in lines:
        print(line)


def handler(event: dict, context):
    for record in event['Records']:                  
        bucket_name = record['s3']['bucket']['name']         
        object_key = record['s3']['object']['key']
        write_listings_csv_to_db(bucket_name, object_key) 
