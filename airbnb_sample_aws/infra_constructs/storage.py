""" Building block for storage services """

from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    RemovalPolicy,
)


class StorageService(Construct):
    """ Storage related Construct """
    def __init__(self, scope: Construct, id: str,
                 database_name: str,
                 vpc: ec2.IVpc
                ) -> None:
        """
        Parameters:
        database_name (str): Name of your database to access
        vpc (IVpc): VPC that RDS is going to be set up in it
        """
        super().__init__(scope, id)

        # Main database
        self.rds_instance = rds.DatabaseInstance(
            self,
            'DBInstance',
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_26),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            database_name=database_name,
        )
