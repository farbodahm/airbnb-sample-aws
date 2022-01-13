""" Building block for /rooms and all its resources. """

from typing import List
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    custom_resources as cr,
    aws_logs as logs,
    aws_rds as rds,
    aws_apigateway as apigateway,
    CfnOutput,
)


class RoomsApiService(Construct):
    """ All /rooms related infrastructures """
    def __init__(self, scope: Construct, id: str,
                 vpc: ec2.IVpc,
                 rds_instance: rds.DatabaseInstance,
                 layers: List[lambda_.ILayerVersion],
                ):
        """
        Parameters:
        vpc (IVpc): Vpc that the database is in it.
        rds_instance (DatabaseInstance): RDS database instance to grant permissions.
        layers (List[ILayerVersion]): Layers that are needed to be associated with lambdas.
        """
        super().__init__(scope, id)

        # Lambda function for processing GET requests
        process_get_func = lambda_.Function(
            self, 
            'ProcessGet',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='get.handler',
            code=lambda_.Code.from_asset('./lambda/api/rooms'),
            vpc=vpc,
            layers=layers,
            environment={'DB_SECRET_MANAGER_ARN': rds_instance.secret.secret_arn}
        )

        # Main Api Gateway for /rooms
        api = apigateway.RestApi(
            self,
            'rooms-api',
        )

        rooms = api.root.add_resource('rooms')
        rooms.add_method(
            'GET',
            integration=apigateway.LambdaIntegration(
                process_get_func,
                proxy=True,
            )
        )

        # Create an Output for the API URL
        CfnOutput(
            self,
            'roomsApi',
            value=api.url,
            description='URL of the /rooms API'
        )