""" Building block for ingesting uploaded CSVs to DB """

from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_s3_notifications as s3_notify,
    aws_rds as rds,
    Duration,
)


class CsvMigrationService(Construct):
    """ Migrate uploaded S3 CSVs to DB """
    def __init__(self, scope: Construct, id: str,
                 vpc: ec2.IVpc,
                 rds_instance: rds.DatabaseInstance,
                 csv_bucket_arn: str,
                 layers: Sequence[lambda_.ILayerVersion],
                 lambda_memory_size: int = 512,
                 lambda_timeout_seconds: int = 360,
                ):
        """
        Parameters:
        vpc (IVpc): Vpc that the database is in it.
        rds_instance (DatabaseInstance): RDS database instance to grant permissions.
        csv_bucket_arn (str): ARN of S3 bucket that contains CSVs.
        layers (Sequence[ILayerVersion]): Layers that are needed to be associated with lambdas.
        lambda_memory_size (int): Maximum memory allowed for processing CSVs in MBs.
        lambda_timeout_seconds (int): Maximum time allowed for processing CSVs in seconds.
        Notes:
        * Sould get S3 bucket ARN instead of it's instance, otherwise it will be a cyclic reference.
        """
        super().__init__(scope, id)

        # Create a lambda function for processing uploaded CSVs
        process_func = lambda_.Function(
            self,
            'ProcessCSV',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='process_csv.handler',
            code=lambda_.Code.from_asset('./lambda/process_csv'),
            vpc=vpc,
            layers=layers,
            memory_size=lambda_memory_size,
            timeout=Duration.seconds(lambda_timeout_seconds),
            environment={'DB_SECRET_MANAGER_ARN': rds_instance.secret.secret_arn}
        )

        # S3 bucket that contains CSVs
        csv_bucket = s3.Bucket.from_bucket_arn(
            self,
            'CsvBucketFromArn',
            csv_bucket_arn,
        )

        # Create trigger for Lambda function using suffix
        notification = s3_notify.LambdaDestination(process_func)
        notification.bind(self, csv_bucket)

        # Add Create Event only for .csv files
        csv_bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(suffix='.csv')
        )

        csv_bucket.grant_read(process_func)

        # Grant DB connection access to Lambda function
        process_func.connections.allow_to(rds_instance, ec2.Port.tcp(3306))
        rds_instance.secret.grant_read(process_func)
        rds_instance.grant_connect(process_func)
