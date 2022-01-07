from aws_cdk import (
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3_notify,
    aws_ec2 as ec2,
    aws_rds as rds,
    Stack,
)
from constructs import Construct


DATABASE_NAME = 'airbnb'

class ImportCsvStack(Stack):
    """ Stack for creating infrastructure of migrating Airbnb
    data sets to DB.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # RDS needs to be setup in a VPC
        vpc = ec2.Vpc(self, 'migrate-csv-vpc', max_azs=1)

        # Create bucket for storing CSVs
        csv_bucket = s3.Bucket(self,
                               'CSV-Bucket',
                               removal_policy=RemovalPolicy.DESTROY)

        rds_instance = rds.DatabaseInstance(self,
                                            'DBInstance',
                                            engine=rds.DatabaseInstanceEngine.mysql(
                                                version=rds.MysqlEngineVersion.VER_8_0_26),
                                            instance_type=ec2.InstanceType.of(
                                                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
                                            ),
                                            vpc=vpc,
                                            removal_policy=RemovalPolicy.DESTROY,
                                            deletion_protection=False,
                                            database_name=DATABASE_NAME)

        # Create a lambda function for processing uploaded CSVs
        process_func = lambda_.Function(self, 'ProcessCSV',
                       runtime=lambda_.Runtime.PYTHON_3_9,
                       handler='process_csv.handler',
                       code=lambda_.Code.from_asset('./lambda'),
                       vpc=vpc,
                       environment={'BUCKET_NAME': csv_bucket.bucket_name})

        # Create trigger for Lambda function using suffix
        notification = s3_notify.LambdaDestination(process_func)
        notification.bind(self, csv_bucket)

        # Add Create Event only for .jpg files
        csv_bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(suffix='.csv'))

        csv_bucket.grant_read(process_func)