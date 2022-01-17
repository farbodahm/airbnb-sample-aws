from typing import List
from constructs import Construct
from aws_cdk import (
    Stack,
)

from airbnb_sample_aws.infra_constructs import (
    layers,
    network,
)


class InfraStack(Stack):
    """ Infrastructure of the main app
    """

    def __init__(self, scope: Construct, construct_id: str,
                 vpc_id: str = None,
                 **kwargs) -> None:
        """
        Parameters:
        vpc_id (str): If you want to use your own VPC that has at least 1 Public and 1 Private subnets
        """
        super().__init__(scope, construct_id, **kwargs)

        self.layers_construct = layers.LayersService(
            self,
            'LayersConstruct',
        )

        self.network_construct = network.NetworkService(
            self,
            'NetworkCOnstruct',
            vpc_id,
        )
