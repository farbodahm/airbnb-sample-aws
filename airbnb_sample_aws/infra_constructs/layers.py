""" Contains all Lambda layers """

from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
)


class LayersService(Construct):
    """ Lambda Layers Construct """
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        # PyMySql Lambda layer
        self.pymysql_lambda_layer = lambda_.LayerVersion(
            self,
            'PymysqlLambdaLayer',
            code=lambda_.Code.from_asset('./layers/pymysql.zip'),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description='PyMySql Library',
        )
