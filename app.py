#!/usr/bin/env python3

import aws_cdk as cdk

from airbnb_sample_aws.import_csv_stack import ImportCsvStack


app = cdk.App()
stack1 = ImportCsvStack(app, 'ImportCsvStack')

cdk.Tags.of(stack1).add('owner', 'farbod')

app.synth()
