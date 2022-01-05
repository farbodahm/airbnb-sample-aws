from aws_cdk import (
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3_notify,
    Stack,
)
from constructs import Construct

class ImportCsvStack(Stack):
    """ Stack for creating infrastructure of migrating Airbnb
    data sets to DB.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create bucket for storing CSVs
        csv_bucket = s3.Bucket(self, 'CSV-Bucket')

        # Create a lambda function for processing uploaded CSVs
        process_func = lambda_.Function(self, 'ProcessCSV',
                       runtime=lambda_.Runtime.PYTHON_3_9,
                       handler='process_csv.handler',
                       code=lambda_.Code.from_asset('./lambda'),
                       environment={'BUCKET_NAME': csv_bucket.bucket_name})

        # Create trigger for Lambda function using suffix
        notification = s3_notify.LambdaDestination(process_func)
        notification.bind(self, csv_bucket)

        # Add Create Event only for .jpg files
        csv_bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(suffix='.csv'))

        csv_bucket.grant_read(process_func)