""" Building block for DB """

from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_lambda as lambda_,
    RemovalPolicy,
)


class DatabaseService(Construct):
    """ Main RDS Construct """
    def __init__(self, scope: Construct, id: str, database_name: str, vpc_id: str = None):
        """
        Parameters:
        database_name (str): Name of your database to access
        vpc_id (str): If you want to use your own VPC that has at least 1 Public and 1 Private subnets
        """
        super().__init__(scope, id)


        # RDS needs to be setup in a VPC
        self.vpc: ec2.IVpc
        if vpc_id is None:
            self.vpc = ec2.Vpc(self, 'migrate-csv-vpc', nat_gateways=1,)
        else:
            self.vpc = ec2.Vpc.from_lookup(self, 'migrate-csv-vpc', vpc_id=vpc_id,)

        # Main database
        self.rds_instance = rds.DatabaseInstance(
            self,
            'DBInstance',
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_26),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            vpc=self.vpc,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            database_name=database_name,
        )

