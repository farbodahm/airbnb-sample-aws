""" Building block for /calendars and all its resources. """

from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_apigateway as apigateway,
    CfnOutput,
)


class CalendarsApiService(Construct):
    """ All /calendars related infrastructures """
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

        # Lambda function for processing GET requests
        process_get_func = lambda_.Function(
            self, 
            'ProcessGet',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='get.handler',
            code=lambda_.Code.from_asset('./lambda/api/calendars'),
            vpc=vpc,
            layers=layers,
            environment={'DB_SECRET_MANAGER_ARN': rds_instance.secret.secret_arn}
        )

        # Main Api Gateway for /calendars
        api = apigateway.RestApi(
            self,
            'calendars-api',
        )

        calendars = api.root.add_resource('calendars')
        calendars.add_method(
            'GET',
            integration=apigateway.LambdaIntegration(
                process_get_func,
                proxy=True,
            ),
        )

        # rds_instance.connections.allow_from(process_get_func, ec2.Port.tcp(3306))
        process_get_func.connections.allow_to(rds_instance, ec2.Port.tcp(3306))
        rds_instance.secret.grant_read(process_get_func)
        rds_instance.grant_connect(process_get_func)

  
        # Create an Output for the API URL
        CfnOutput(
            self,
            'calendarsApi',
            value=api.url,
            description='URL of the /calendars API',
        )