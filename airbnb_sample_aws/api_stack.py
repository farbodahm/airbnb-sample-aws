from typing import Sequence
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_sqs as sqs,
)


from airbnb_sample_aws.api_constructs import (
    calendars,
)


class ApiStack(Stack):
    """ Stack for API infrastructure.
    """

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 rds_instance: rds.DatabaseInstance,
                 layers: Sequence[lambda_.ILayerVersion],
                 post_calendars_queue: sqs.IQueue,
                 **kwargs
                ) -> None:
        """
        Parameters:
        vpc (IVpc): Vpc that the database is in it.
        rds_instance (DatabaseInstance): RDS database instance to grant permissions.
        layers (Sequence[ILayerVersion]): Layers that are needed to be associated with lambdas.
        """
        super().__init__(scope, construct_id, **kwargs)

        calendars.CalendarsApiService(
            self,
            'calendars-construct',
            vpc,
            rds_instance,
            layers,
            post_calendars_queue,
        )
