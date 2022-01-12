#!/usr/bin/env python3

import aws_cdk as cdk

from airbnb_sample_aws.import_csv_stack import ImportCsvStack


ENV_EU = cdk.Environment(account='YOUR-ACCOUNT-ID', region='YOUR-REGION')


app = cdk.App()
stack1 = ImportCsvStack(app, 'ImportCsvStack', env=ENV_EU)

cdk.Tags.of(stack1).add('owner', 'farbod')

app.synth()
