""" Building block for initializing DB during deployment using Custom Resources. """

from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    custom_resources as cr,
    aws_logs as logs,
    aws_rds as rds,
    CustomResource,
)


class DbInitializerService(Construct):
    """ Initialize DB during deployment """
    def __init__(self, scope: Construct, id: str,
                 vpc: ec2.IVpc,
                 rds_instance: rds.DatabaseInstance,
                 layers: Sequence[lambda_.ILayerVersion],
                 ):
        """
        Parameters:
        vpc (IVpc): Vpc that the database is in it.
        rds_instance (DatabaseInstance): RDS database instance to grant permissions.
        layers (Sequence[ILayerVersion]): Layers that are needed to be associated with lambdas.
        """
        super().__init__(scope, id)

        # Create a lambda function for initializing database on creation
        db_initialize_func = lambda_.Function(
            self, 
            'InitializeDB',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='initialize_db.handler',
            code=lambda_.Code.from_asset('./lambda/process_csv'),
            vpc=vpc,
            layers=layers,
            environment={'DB_SECRET_MANAGER_ARN': rds_instance.secret.secret_arn}
        )

        # Create Custom Resource to update database schema
        provider1 = cr.Provider(
            self,
            'DbInitializeProvider',
            on_event_handler=db_initialize_func,
            log_retention=logs.RetentionDays.ONE_DAY,
            vpc=vpc,
        )
        CustomResource(self, 'Resource1', service_token=provider1.service_token)

        # Grant DB connection access to Lambda function
        db_initialize_func.connections.allow_to(rds_instance, ec2.Port.tcp(3306))
        rds_instance.secret.grant_read(db_initialize_func)
        rds_instance.grant_connect(db_initialize_func)
