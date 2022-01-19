""" Building block for /calendars and all its resources. """

from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_apigateway as apigateway,
    aws_sqs as sqs,
    aws_lambda_event_sources,
    aws_iam as iam,
    CfnOutput,
    Aws,
)


class CalendarsApiService(Construct):
    """ All /calendars related infrastructures """
    def __init__(self, scope: Construct, id: str,
                 vpc: ec2.IVpc,
                 rds_instance: rds.DatabaseInstance,
                 layers: Sequence[lambda_.ILayerVersion],
                 post_calendars_queue: sqs.IQueue,
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

        # Lambda function for processing POST requests
        process_post_func = lambda_.Function(
            self, 
            'ProcessPost',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='post.handler',
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

        # Role for ApiGatewat to send requests to SQS        
        apigateway_to_sqs_role = iam.Role(
            self,
            'ApiGatewayToSqsRole',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com')
        )
        apigateway_to_sqs_role.attach_inline_policy(
            iam.Policy(
                self,
                'SendMessagePolicy',
                statements=[
                    iam.PolicyStatement(
                        actions=['sqs:SendMessage',],
                        effect=iam.Effect.ALLOW,
                        resources=[post_calendars_queue.queue_arn,],
                    ),
                ],
            )
        )

        # Send POST requests to SQS queue
        calendars.add_method(
            'POST',
            integration=apigateway.AwsIntegration(
                service='sqs',
                path=f'{Aws.ACCOUNT_ID}/{post_calendars_queue.queue_name}',
                integration_http_method='POST',
                options=apigateway.IntegrationOptions(
                    credentials_role=apigateway_to_sqs_role,
                    passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
                    request_parameters={
                        'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'",
                    },
                    request_templates={
                        'application/json': 'Action=SendMessage&MessageBody=$input.body',
                    },
                    integration_responses=[
                        apigateway.IntegrationResponse(
                            status_code='200',
                            response_templates={
                                "application/json": '{"done": true}',
                            },
                        ),
                    ],
                ),
            ),
            method_responses=[
                apigateway.MethodResponse(
                    status_code='200',
                ),
            ],
        )
        new_requests_event = aws_lambda_event_sources.SqsEventSource(
            post_calendars_queue,
        )
        process_post_func.add_event_source(new_requests_event)

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
