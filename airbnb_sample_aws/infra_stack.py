from typing import List
from constructs import Construct
from aws_cdk import (
    Stack,
)

from airbnb_sample_aws.infra_constructs import (
    layers,
)


class InfraStack(Stack):
    """ Infrastructure of the main app
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.layers_construct = layers.LayersService(
            self,
            'LayersConstruct',
        )
