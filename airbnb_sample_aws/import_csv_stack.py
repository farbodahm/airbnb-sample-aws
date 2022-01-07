from aws_cdk import (
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3_notify,
    aws_ec2 as ec2,
    aws_rds as rds,
    custom_resources as cr,
    CustomResource,
    aws_logs as logs,
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
        vpc = ec2.Vpc(self, 'migrate-csv-vpc', max_azs=2)

        # Create bucket for storing CSVs
        csv_bucket = s3.Bucket(self,
                               'CSV-Bucket',
                               removal_policy=RemovalPolicy.DESTROY)

        # Main database
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

        # PyMySql Lambda layer
        pymysql_lambda_layer = lambda_.LayerVersion(
               self, 'MymysqlLambdaLayer',
               code=lambda_.Code.from_asset('./layers/pymysql.zip'),
               compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
               description='PyMySql Library',
            )

        # Create a lambda function for initializing database on creation
        db_initialize_func = lambda_.Function(self, 'InitializeDB',
                       runtime=lambda_.Runtime.PYTHON_3_9,
                       handler='initialize_db.handler',
                       code=lambda_.Code.from_asset('./lambda'),
                       vpc=vpc,
                       layers=[pymysql_lambda_layer,],
                       environment={'DB_SECRET_MANAGER_ARN': rds_instance.secret.secret_arn})

        # Grant DB connection access to Lambda function
        rds_instance.connections.allow_from(db_initialize_func, ec2.Port.tcp(3306))
        rds_instance.secret.grant_read(db_initialize_func)
        rds_instance.grant_connect(db_initialize_func)

        # Create Custom Resource to update database schema
        my_provider = cr.Provider(self,
                                  'DbInitializeProvider',
                                  on_event_handler=db_initialize_func,
                                  log_retention=logs.RetentionDays.ONE_DAY,
                                  vpc=vpc,)
        CustomResource(self, 'Resource1', service_token=my_provider.service_token)

        # Create a lambda function for processing uploaded CSVs
        process_func = lambda_.Function(self, 'ProcessCSV',
                       runtime=lambda_.Runtime.PYTHON_3_9,
                       handler='process_csv.handler',
                       code=lambda_.Code.from_asset('./lambda'),
                       vpc=vpc,
                       layers=[pymysql_lambda_layer,],
                       environment={'DB_SECRET_MANAGER_ARN': rds_instance.secret.secret_arn})

        # Create trigger for Lambda function using suffix
        notification = s3_notify.LambdaDestination(process_func)
        notification.bind(self, csv_bucket)

        # Add Create Event only for .csv files
        csv_bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(suffix='.csv'))

        # Permissions for process_func lambda
        csv_bucket.grant_read(process_func)
        rds_instance.connections.allow_from(process_func, ec2.Port.tcp(3306))
        rds_instance.secret.grant_read(process_func)
        rds_instance.grant_connect(process_func)