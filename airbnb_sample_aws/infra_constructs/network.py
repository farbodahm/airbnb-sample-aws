""" Building block of network related parts of the project """

from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
)


class NetworkService(Construct):
    """ Network infra Construct """
    def __init__(self, scope: Construct, id: str, vpc_id: str) -> None:
        """
        Parameters:
        vpc_id (str): If you want to use your own VPC that has at least 1 Public and 1 Private subnets
        """
        super().__init__(scope, id)

        # RDS needs to be setup in a VPC
        self.vpc: ec2.IVpc
        if vpc_id is None:
            self.vpc = ec2.Vpc(self, 'migrate-csv-vpc', nat_gateways=1,)
        else:
            self.vpc = ec2.Vpc.from_lookup(self, 'migrate-csv-vpc', vpc_id=vpc_id,)
