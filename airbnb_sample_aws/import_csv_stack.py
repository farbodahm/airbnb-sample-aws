from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
)


from airbnb_sample_aws.import_csv_constructs import (
    db_initialize,
    process_csv,
)


class ImportCsvStack(Stack):
    """ Stack for creating infrastructure of migrating Airbnb
    data sets to DB.
    """

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 rds_instance: rds.DatabaseInstance,
                 layers: Sequence[lambda_.ILayerVersion],
                 **kwargs) -> None:
        """
        Parameters:
        vpc (IVpc): Vpc that the database is in it.
        rds_instance (DatabaseInstance): RDS database instance to grant permissions.
        layers (Sequence[ILayerVersion]): Layers that are needed to be associated with lambdas.
        """
        super().__init__(scope, construct_id, **kwargs)

        db_initialize.DbInitializerService(
            self,
            'db-initialize-construct',
            vpc,
            rds_instance,
            layers,
        )

        process_csv.CsvMigrationService(
            self,
            'process-csv-construct',
            vpc,
            rds_instance,
            layers,
        )
