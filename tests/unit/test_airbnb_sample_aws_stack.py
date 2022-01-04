import aws_cdk as core
import aws_cdk.assertions as assertions

from airbnb_sample_aws.airbnb_sample_aws_stack import AirbnbSampleAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in airbnb_sample_aws/airbnb_sample_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AirbnbSampleAwsStack(app, "airbnb-sample-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
