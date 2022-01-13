#!/usr/bin/env python3

from inspect import stack
import aws_cdk as cdk

from airbnb_sample_aws.import_csv_stack import ImportCsvStack
from airbnb_sample_aws.api_stack import ApiStack

ENV_EU = cdk.Environment(account='YOUR-ACCOUNT-ID', region='YOUR-REGION')


app = cdk.App()
stack1 = ImportCsvStack(app, 'ImportCsvStack', env=ENV_EU)
stack2 = ApiStack(
    app, 
    'ApiStack',
    stack1.db_construct.vpc,
    stack1.db_construct.rds_instance,
    [stack1.db_construct.pymysql_lambda_layer,],
    env=ENV_EU
)

cdk.Tags.of(stack1).add('owner', 'farbod')
cdk.Tags.of(stack2).add('owner', 'farbod')


app.synth()
