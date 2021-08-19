import json
import logging
from logging.config import dictConfig

from flask import Flask
from flask_restful import Api, Resource

import datetime
from uuid import uuid4

import boto3

# configure queue
sqs = boto3.resource("sqs")
queue = sqs.Queue(
    "https://sqs.eu-west-3.amazonaws.com/571825886228/sqs-Boost-Test.fifo"
)

# configure logging
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "default",
                "level": "ERROR",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["stderr", "stdout"]},
    }
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)


def send_message_to_sqs(_id=None):
    if _id is None:
        _id = uuid4().hex
    queue.send_message(
        MessageBody=json.dumps(
            {"id": _id, "timestamp": f"{datetime.datetime.now().isoformat()}"}
        ),
        MessageDeduplicationId=_id,
        MessageGroupId="asset",
    )


def construct_response(message, status_code=200):
    envelope = {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "body": json.dumps(message),
    }
    logger.info("Response: " + str(envelope)[:256])
    return envelope


class Handler(Resource):
    def get(self):
        _id = uuid4().hex
        logger.info(f"Sending message to SQS with id {_id}")
        send_message_to_sqs(_id)
        return construct_response({"id": _id})


api.add_resource(Handler, "/")

if __name__ == "__main__":
    app.run(debug=False)
