""" Building block of messaging services """

from constructs import Construct
from aws_cdk import (
    aws_sqs as sqs,
    Duration,
)


class MessagingService(Construct):
    """ Messaging services Construct """
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.post_calendars_queue = sqs.Queue(
            self,
            'PostCalendarsQueue',
            receive_message_wait_time=Duration.seconds(19),  # To reduce the cost of SQS
        )
