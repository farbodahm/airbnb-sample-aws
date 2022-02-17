from typing import List
from constructs import Construct
from aws_cdk import (
    Stack,
)

from airbnb_sample_aws.infra_constructs import (
    layers,
    network,
    storage,
    db_initialize,
    messaging,
    glue_crawler,
)


class InfraStack(Stack):
    """ Infrastructure of the main app
    """

    def __init__(self, scope: Construct, construct_id: str,
                 database_name: str,
                 vpc_id: str = None,
                 **kwargs) -> None:
        """
        Parameters:
        database_name (str): Name of your database to access
        vpc_id (str): If you want to use your own VPC that has at least 1 Public and 1 Private subnets
        """
        super().__init__(scope, construct_id, **kwargs)

        self.layers_construct = layers.LayersService(
            self,
            'LayersConstruct',
        )

        self.network_construct = network.NetworkService(
            self,
            'NetworkConstruct',
            vpc_id,
        )

        self.storage_construct = storage.StorageService(
            self,
            'StorageService',
            database_name,
            self.network_construct.vpc,
        )

        self.messaging_construct = messaging.MessagingService(
            self,
            'MessagingConstruct',
        )

        db_initialize.DbInitializerService(
            self,
            'db-initialize-construct',
            self.network_construct.vpc,
            self.storage_construct.rds_instance,
            [self.layers_construct.pymysql_lambda_layer,],
        )

        # TODO: Create required S3 bucket with Glue DataBrew
        glue_crawler.GlueCrawlerService(
            self,
            'GlueCrawlerConstruct',
            'YOUR_S3_ARN',
            'CSV_FILES_PATH',
        )
