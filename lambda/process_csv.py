""" Migrate Airbnb CSVs to DB uploaded to S3. """

def handler(event: dict, context):
    print(type(event))
    print(type(context))
    print(event)