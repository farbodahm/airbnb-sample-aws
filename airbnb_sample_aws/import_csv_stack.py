from constructs import Construct
from aws_cdk import (
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

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.db_construct = db.DatabaseService(
            self, 
            'db-construct',
            'airbnb',
        )

        db_initialize_construct = db_initialize.DbInitializerService(
            self,
            'db-initialize-construct',
            self.db_construct.vpc,
            self.db_construct.rds_instance,
            [self.db_construct.pymysql_lambda_layer,],
        )

        process_csv_construct = process_csv.CsvMigrationService(
            self,
            'process-csv-construct',
            self.db_construct.vpc,
            self.db_construct.rds_instance,
            [self.db_construct.pymysql_lambda_layer,],
        )
