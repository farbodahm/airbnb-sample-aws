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
    'airbnb',
    env=ENV_EU
)
import_csv_stack = ImportCsvStack(
    app,
    'ImportCsvStack',
    infra_stack.network_construct.vpc,
    infra_stack.storage_construct.rds_instance,
    infra_stack.storage_construct.csv_bucket.bucket_arn,
    [infra_stack.layers_construct.pymysql_lambda_layer,],
    env=ENV_EU
)
api_stack = ApiStack(
    app, 
    'ApiStack',
    infra_stack.network_construct.vpc,
    infra_stack.storage_construct.rds_instance,
    [infra_stack.layers_construct.pymysql_lambda_layer,],
    env=ENV_EU
)

cdk.Tags.of(import_csv_stack).add('owner', 'farbod')
cdk.Tags.of(api_stack).add('owner', 'farbod')
cdk.Tags.of(infra_stack).add('owner', 'farbod')


app.synth()
