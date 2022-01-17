from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    Stack,
    aws_ec2 as ec2,
)


from airbnb_sample_aws.import_csv_constructs import (
    db_initialize,
    db,
    process_csv,
)


class ImportCsvStack(Stack):
    """ Stack for creating infrastructure of migrating Airbnb
    data sets to DB.
    """

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 layers: Sequence[lambda_.ILayerVersion],
                 **kwargs) -> None:
        """
        Parameters:
        layers (Sequence[ILayerVersion]): Layers that are needed to be associated with lambdas.
        """
        super().__init__(scope, construct_id, **kwargs)

        self.db_construct = db.DatabaseService(
            self, 
            'db-construct',
            'airbnb',
            vpc,
        )

        db_initialize.DbInitializerService(
            self,
            'db-initialize-construct',
            vpc,
            self.db_construct.rds_instance,
            layers,
        )

        process_csv.CsvMigrationService(
            self,
            'process-csv-construct',
            vpc,
            self.db_construct.rds_instance,
            layers,
        )
