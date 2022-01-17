from typing import Sequence
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    Stack,
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
        )

        db_initialize.DbInitializerService(
            self,
            'db-initialize-construct',
            self.db_construct.vpc,
            self.db_construct.rds_instance,
            layers,
        )

        process_csv.CsvMigrationService(
            self,
            'process-csv-construct',
            self.db_construct.vpc,
            self.db_construct.rds_instance,
            layers,
        )
