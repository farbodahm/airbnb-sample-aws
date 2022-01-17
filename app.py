#!/usr/bin/env python3

from inspect import stack
import aws_cdk as cdk

from airbnb_sample_aws.import_csv_stack import ImportCsvStack
from airbnb_sample_aws.api_stack import ApiStack
from airbnb_sample_aws.infra_stack import InfraStack

ENV_EU = cdk.Environment(account='YOUR-ACCOUNT-ID', region='YOUR-REGION')


app = cdk.App()
infra_stack = InfraStack(
    app,
    'InfraStack',
    env=ENV_EU
)
stack1 = ImportCsvStack(
    app,
    'ImportCsvStack',
    [infra_stack.layers_construct.pymysql_lambda_layer,],
    env=ENV_EU
)
stack2 = ApiStack(
    app, 
    'ApiStack',
    stack1.db_construct.vpc,
    stack1.db_construct.rds_instance,
    [infra_stack.layers_construct.pymysql_lambda_layer,],
    env=ENV_EU
)

cdk.Tags.of(stack1).add('owner', 'farbod')
cdk.Tags.of(stack2).add('owner', 'farbod')
cdk.Tags.of(infra_stack).add('owner', 'farbod')


app.synth()
