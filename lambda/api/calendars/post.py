import json

def handler(event: dict, context):
    print(event)

    body = {
        "message": "HI!"
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }